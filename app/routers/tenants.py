from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.models.tenant import Tenant, TenantDocument
from app.models.room import Bed
from app.schemas.tenant import (
    TenantResponse, TenantDetailResponse, TenantCreate, TenantUpdate,
    TenantDocumentCreate, TenantDocumentResponse, TenantCheckout
)

router = APIRouter(prefix="/tenants", tags=["Tenants & KYC"])

@router.get("", response_model=List[TenantResponse])
def list_tenants(
    is_active: Optional[bool] = Query(None, description="Filter by active tenancy"),
    kyc_status: Optional[str] = Query(None, description="Filter by KYC status (PENDING, VERIFIED, REJECTED)"),
    search: Optional[str] = Query(None, description="Search by name or phone number"),
    db: Session = Depends(get_db)
):
    """List tenants with optional filters for active status, KYC status, and search keyword."""
    query = db.query(Tenant)
    if is_active is not None:
        query = query.filter(Tenant.is_active == is_active)
    if kyc_status:
        query = query.filter(Tenant.kyc_status == kyc_status.upper())
    if search:
        search_pattern = f"%{search}%"
        query = query.filter((Tenant.full_name.ilike(search_pattern)) | (Tenant.phone.ilike(search_pattern)))
    return query.all()


@router.post("/onboard", response_model=TenantDetailResponse, status_code=status.HTTP_201_CREATED)
def onboard_tenant(tenant_in: TenantCreate, db: Session = Depends(get_db)):
    """Onboard a new tenant into the PG, allocate a bed slot, and lock bed as OCCUPIED."""
    # Check duplicate phone
    existing = db.query(Tenant).filter(Tenant.phone == tenant_in.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant with phone number '{tenant_in.phone}' already exists."
        )

    # Validate bed if assigned
    if tenant_in.bed_id:
        bed = db.query(Bed).filter(Bed.id == tenant_in.bed_id).first()
        if not bed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified bed not found.")
        if bed.status != "AVAILABLE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bed '{bed.bed_number}' is not available for assignment (Current status: {bed.status})."
            )
        bed.status = "OCCUPIED"

    tenant = Tenant(
        full_name=tenant_in.full_name,
        phone=tenant_in.phone,
        email=tenant_in.email,
        emergency_contact_name=tenant_in.emergency_contact_name,
        emergency_contact_phone=tenant_in.emergency_contact_phone,
        permanent_address=tenant_in.permanent_address,
        occupation=tenant_in.occupation,
        id_proof_type=tenant_in.id_proof_type,
        id_proof_number=tenant_in.id_proof_number,
        security_deposit=tenant_in.security_deposit,
        check_in_date=tenant_in.check_in_date or date.today(),
        bed_id=tenant_in.bed_id,
        is_active=True,
        kyc_status="PENDING"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=TenantDetailResponse)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    """Retrieve full details of a tenant including uploaded KYC documents."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(tenant_id: int, tenant_in: TenantUpdate, db: Session = Depends(get_db)):
    """Update tenant information, change KYC status, or re-allocate beds."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    update_data = tenant_in.model_dump(exclude_unset=True)

    # Handle bed reallocation
    if "bed_id" in update_data and update_data["bed_id"] != tenant.bed_id:
        new_bed_id = update_data["bed_id"]
        # Free old bed
        if tenant.bed_id:
            old_bed = db.query(Bed).filter(Bed.id == tenant.bed_id).first()
            if old_bed:
                old_bed.status = "AVAILABLE"

        # Claim new bed if specified
        if new_bed_id:
            new_bed = db.query(Bed).filter(Bed.id == new_bed_id).first()
            if not new_bed:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target bed not found.")
            if new_bed.status != "AVAILABLE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target bed '{new_bed.bed_number}' is not available (Current status: {new_bed.status})."
                )
            new_bed.status = "OCCUPIED"

    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    """Delete a tenant. Releases allocated bed and removes tenant profile and associated records."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    if tenant.bed_id:
        bed = db.query(Bed).filter(Bed.id == tenant.bed_id).first()
        if bed:
            bed.status = "AVAILABLE"
        tenant.bed_id = None

    db.delete(tenant)
    db.commit()
    return None


@router.post("/{tenant_id}/documents", response_model=TenantDocumentResponse, status_code=status.HTTP_201_CREATED)
def add_tenant_document(tenant_id: int, doc_in: TenantDocumentCreate, db: Session = Depends(get_db)):
    """Record an uploaded KYC document or ID proof for the tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    doc = TenantDocument(
        tenant_id=tenant.id,
        document_name=doc_in.document_name,
        document_path_or_url=doc_in.document_path_or_url
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/{tenant_id}/checkout", response_model=TenantResponse)
def checkout_tenant(tenant_id: int, checkout_data: TenantCheckout, db: Session = Depends(get_db)):
    """Check out a tenant: sets inactive, records checkout date, and releases their bed to AVAILABLE."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    if not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant is already checked out.")

    # Free up the allocated bed
    if tenant.bed_id:
        bed = db.query(Bed).filter(Bed.id == tenant.bed_id).first()
        if bed:
            bed.status = "AVAILABLE"
        tenant.bed_id = None

    tenant.is_active = False
    tenant.check_out_date = checkout_data.check_out_date or date.today()

    db.commit()
    db.refresh(tenant)
    return tenant

