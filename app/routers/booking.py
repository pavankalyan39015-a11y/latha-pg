from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import quote
from datetime import date

from app.database import get_db
from app.models.booking import BookingInquiry
from app.models.room import Bed, Room
from app.models.tenant import Tenant
from app.schemas.booking import (
    BookingInquiryCreate,
    BookingInquiryUpdate,
    BookingInquiryResponse,
    ConvertToTenantRequest,
)
from app.schemas.tenant import TenantDetailResponse

router = APIRouter(prefix="/bookings", tags=["Bookings & Inquiries"])

PG_PHONE_PRIMARY = "919353439703"

@router.post("/inquire", response_model=dict, status_code=status.HTTP_201_CREATED)
def submit_booking_inquiry(inquiry_in: BookingInquiryCreate, db: Session = Depends(get_db)):
    """
    Public endpoint for prospective tenants to inquire about bed booking.
    Generates a unique reference code and returns details plus a WhatsApp link.
    """
    ref_code = BookingInquiry.generate_reference_code()
    
    # Ensure reference code uniqueness
    while db.query(BookingInquiry).filter(BookingInquiry.reference_code == ref_code).first():
        ref_code = BookingInquiry.generate_reference_code()

    inquiry = BookingInquiry(
        reference_code=ref_code,
        full_name=inquiry_in.full_name.strip(),
        phone=inquiry_in.phone.strip(),
        email=inquiry_in.email.strip() if inquiry_in.email else None,
        room_type=inquiry_in.room_type,
        sharing_preference=inquiry_in.sharing_preference,
        preferred_move_in_date=inquiry_in.preferred_move_in_date,
        notes=inquiry_in.notes,
        status="NEW"
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    # Pre-compose WhatsApp message
    msg = (
        f"Hello Latha PG Manager, I have submitted an inquiry for room booking.\n\n"
        f"📋 Ref Code: {inquiry.reference_code}\n"
        f"👤 Name: {inquiry.full_name}\n"
        f"📞 Phone: {inquiry.phone}\n"
        f"🛏️ Preference: {inquiry.sharing_preference} ({inquiry.room_type})\n"
        f"📅 Move-in Date: {inquiry.preferred_move_in_date}\n\n"
        f"Please let me know room availability and viewing schedule. Thank you!"
    )
    whatsapp_url = f"https://wa.me/{PG_PHONE_PRIMARY}?text={quote(msg)}"

    return {
        "message": "Inquiry submitted successfully! We will get in touch shortly.",
        "inquiry": BookingInquiryResponse.model_validate(inquiry),
        "whatsapp_url": whatsapp_url,
    }


@router.get("", response_model=List[BookingInquiryResponse])
def list_booking_inquiries(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (NEW, CONTACTED, VISITED, BOOKED, CANCELLED)"),
    search: Optional[str] = Query(None, description="Search by name, phone or reference code"),
    db: Session = Depends(get_db)
):
    """List all booking inquiries with optional filtering."""
    query = db.query(BookingInquiry)
    if status_filter:
        query = query.filter(BookingInquiry.status == status_filter.upper())
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (BookingInquiry.full_name.ilike(search_term)) |
            (BookingInquiry.phone.ilike(search_term)) |
            (BookingInquiry.reference_code.ilike(search_term))
        )
    return query.order_by(BookingInquiry.created_at.desc()).all()


@router.get("/{inquiry_id}", response_model=BookingInquiryResponse)
def get_booking_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a specific booking inquiry."""
    inquiry = db.query(BookingInquiry).filter(BookingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking inquiry not found.")
    return inquiry


@router.patch("/{inquiry_id}/status", response_model=BookingInquiryResponse)
def update_inquiry_status(
    inquiry_id: int,
    update_data: BookingInquiryUpdate,
    db: Session = Depends(get_db)
):
    """Update status or notes of a booking inquiry."""
    inquiry = db.query(BookingInquiry).filter(BookingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking inquiry not found.")

    if update_data.status:
        inquiry.status = update_data.status.upper()
    if update_data.notes is not None:
        inquiry.notes = update_data.notes

    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.post("/{inquiry_id}/convert-to-tenant", response_model=TenantDetailResponse, status_code=status.HTTP_201_CREATED)
def convert_inquiry_to_tenant(
    inquiry_id: int,
    req: ConvertToTenantRequest,
    db: Session = Depends(get_db)
):
    """
    1-Click conversion: Turn an accepted inquiry into an active tenant.
    Allocates the specified bed, marks bed OCCUPIED, and sets inquiry status to BOOKED.
    """
    inquiry = db.query(BookingInquiry).filter(BookingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking inquiry not found.")

    # Check if bed is available
    bed = db.query(Bed).filter(Bed.id == req.bed_id).first()
    if not bed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected bed not found.")
    if bed.status != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bed '{bed.bed_number}' is not available (Current status: {bed.status})."
        )

    # Check existing phone to prevent conflict
    existing_tenant = db.query(Tenant).filter(Tenant.phone == inquiry.phone).first()
    if existing_tenant and existing_tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An active tenant with phone '{inquiry.phone}' already exists."
        )

    # Assign bed
    bed.status = "OCCUPIED"

    # Create Tenant record
    tenant = Tenant(
        full_name=inquiry.full_name,
        phone=inquiry.phone,
        email=inquiry.email,
        emergency_contact_name=req.emergency_contact_name,
        emergency_contact_phone=req.emergency_contact_phone,
        permanent_address=req.permanent_address,
        occupation=req.occupation,
        id_proof_type=req.id_proof_type,
        id_proof_number=req.id_proof_number,
        security_deposit=req.security_deposit,
        check_in_date=date.today(),
        bed_id=bed.id,
        is_active=True,
        kyc_status="VERIFIED"
    )
    db.add(tenant)

    # Update inquiry status to BOOKED
    inquiry.status = "BOOKED"
    inquiry.notes = (inquiry.notes or "") + f" [Converted to tenant ID #{tenant.id} with Bed {bed.bed_number}]"

    db.commit()
    db.refresh(tenant)

    # Return TenantDetailResponse with room info populated
    return TenantDetailResponse(
        id=tenant.id,
        full_name=tenant.full_name,
        phone=tenant.phone,
        email=tenant.email,
        emergency_contact_name=tenant.emergency_contact_name,
        emergency_contact_phone=tenant.emergency_contact_phone,
        permanent_address=tenant.permanent_address,
        occupation=tenant.occupation,
        id_proof_type=tenant.id_proof_type,
        id_proof_number=tenant.id_proof_number,
        security_deposit=tenant.security_deposit,
        is_active=tenant.is_active,
        kyc_status=tenant.kyc_status,
        check_in_date=tenant.check_in_date,
        check_out_date=tenant.check_out_date,
        bed_id=tenant.bed_id,
        created_at=tenant.created_at,
        bed=bed,
        room=bed.room,
        documents=[]
    )


@router.delete("/{inquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    """Delete a booking inquiry."""
    inquiry = db.query(BookingInquiry).filter(BookingInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking inquiry not found.")
    db.delete(inquiry)
    db.commit()
    return None
