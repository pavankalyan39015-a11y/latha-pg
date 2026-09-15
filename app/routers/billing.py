from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.database import get_db
from app.models.billing import Invoice, Payment
from app.models.tenant import Tenant
from app.schemas.billing import (
    InvoiceResponse, InvoiceDetailResponse, InvoiceCreate, InvoiceUpdate,
    PaymentResponse, PaymentCreate, TenantDuesResponse
)
from app.utils.receipt_pdf import generate_receipt_pdf_bytes

router = APIRouter(prefix="/billing", tags=["Billing, Rent & Payments"])

@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(
    tenant_id: Optional[int] = Query(None, description="Filter invoices by tenant ID"),
    billing_month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    status: Optional[str] = Query(None, description="Filter by invoice status (UNPAID, PARTIAL, PAID, OVERDUE)"),
    db: Session = Depends(get_db)
):
    """List rent invoices with filtering by tenant, billing month, or payment status."""
    query = db.query(Invoice)
    if tenant_id:
        query = query.filter(Invoice.tenant_id == tenant_id)
    if billing_month:
        query = query.filter(Invoice.billing_month == billing_month)
    if status:
        query = query.filter(Invoice.status == status.upper())
    return query.order_by(Invoice.created_at.desc()).all()


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    """Generate a rent invoice for a tenant. Total is calculated automatically."""
    tenant = db.query(Tenant).filter(Tenant.id == invoice_in.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    # Calculate total
    total = (
        invoice_in.rent_amount
        + invoice_in.utility_charges
        + invoice_in.penalty_charges
        - invoice_in.discount
    )
    if total < 0:
        total = 0.0

    # Auto-generate unique invoice number: INV-YYYYMM-XXXX
    unique_suffix = uuid.uuid4().hex[:6].upper()
    month_clean = invoice_in.billing_month.replace("-", "")
    inv_num = f"INV-{month_clean}-{unique_suffix}"

    invoice = Invoice(
        invoice_number=inv_num,
        tenant_id=invoice_in.tenant_id,
        billing_month=invoice_in.billing_month,
        due_date=invoice_in.due_date,
        rent_amount=invoice_in.rent_amount,
        utility_charges=invoice_in.utility_charges,
        penalty_charges=invoice_in.penalty_charges,
        discount=invoice_in.discount,
        total_amount=total,
        paid_amount=0.0,
        status="UNPAID",
        notes=invoice_in.notes
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Retrieve full invoice details with its associated payment history."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
    return invoice


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, invoice_in: InvoiceUpdate, db: Session = Depends(get_db)):
    """Update invoice details, recalculate total if charges change, or adjust status."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")

    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            setattr(invoice, field, value.upper())
        else:
            setattr(invoice, field, value)

    # Recalculate total if charges changed
    if any(k in update_data for k in ["rent_amount", "utility_charges", "penalty_charges", "discount"]):
        invoice.total_amount = max(0.0, invoice.rent_amount + invoice.utility_charges + invoice.penalty_charges - invoice.discount)
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = "PAID"
        elif invoice.paid_amount > 0:
            invoice.status = "PARTIAL"
        else:
            invoice.status = "UNPAID"

    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    """Record a tenant payment (UPI, Cash, Bank Transfer), issue receipt, and update invoice status."""
    tenant = db.query(Tenant).filter(Tenant.id == payment_in.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    linked_invoice_id = payment_in.invoice_id
    invoice = None
    if linked_invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == linked_invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
    else:
        # Auto-detect pending invoice for this tenant if not explicitly provided
        first_pending = (
            db.query(Invoice)
            .filter(Invoice.tenant_id == payment_in.tenant_id, Invoice.status.in_(["UNPAID", "PARTIAL", "OVERDUE"]))
            .order_by(Invoice.due_date.asc())
            .first()
        )
        if first_pending:
            linked_invoice_id = first_pending.id
            invoice = first_pending

    receipt_num = f"REC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

    payment = Payment(
        receipt_number=receipt_num,
        invoice_id=linked_invoice_id,
        tenant_id=payment_in.tenant_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method.upper(),
        transaction_reference=payment_in.transaction_reference,
        payment_date=payment_in.payment_date or datetime.utcnow(),
        notes=payment_in.notes
    )
    db.add(payment)

    # Settle against invoices
    if payment_in.invoice_id and invoice:
        invoice.paid_amount += payment_in.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = "PAID"
        elif invoice.paid_amount > 0:
            invoice.status = "PARTIAL"
    elif not payment_in.invoice_id:
        # Settle across pending invoices starting from oldest
        remaining_payment = payment_in.amount
        pending_invoices = (
            db.query(Invoice)
            .filter(Invoice.tenant_id == payment_in.tenant_id, Invoice.status.in_(["UNPAID", "PARTIAL", "OVERDUE"]))
            .order_by(Invoice.due_date.asc())
            .all()
        )
        for inv in pending_invoices:
            if remaining_payment <= 0:
                break
            needed = max(0.0, inv.total_amount - inv.paid_amount)
            allocate = min(remaining_payment, needed)
            inv.paid_amount += allocate
            remaining_payment -= allocate
            if inv.paid_amount >= inv.total_amount:
                inv.status = "PAID"
            elif inv.paid_amount > 0:
                inv.status = "PARTIAL"

    db.commit()
    db.refresh(payment)
    return payment



@router.get("/payments", response_model=List[dict])
def list_payments(
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    db: Session = Depends(get_db)
):
    """List payment receipts with tenant names and bed details."""
    query = db.query(Payment)
    if tenant_id:
        query = query.filter(Payment.tenant_id == tenant_id)
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method.upper())
    
    payments = query.order_by(Payment.payment_date.desc()).all()
    results = []
    for p in payments:
        tenant = p.tenant
        bed_num = tenant.bed.bed_number if tenant and tenant.bed else "N/A"
        results.append({
            "id": p.id,
            "receipt_number": p.receipt_number,
            "invoice_id": p.invoice_id,
            "tenant_id": p.tenant_id,
            "tenant_name": tenant.full_name if tenant else f"Tenant #{p.tenant_id}",
            "bed_number": bed_num,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "transaction_reference": p.transaction_reference,
            "payment_date": p.payment_date.isoformat(),
            "notes": p.notes
        })
    return results


@router.get("/payments/{payment_id}/receipt")
def get_payment_receipt(payment_id: int, db: Session = Depends(get_db)):
    """Retrieve full official receipt details for printing and sharing."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment receipt not found.")

    tenant = payment.tenant
    bed_info = tenant.bed.bed_number if (tenant and tenant.bed) else "N/A"
    room_info = tenant.bed.room.room_number if (tenant and tenant.bed and tenant.bed.room) else "N/A"

    return {
        "receipt_number": payment.receipt_number,
        "payment_id": payment.id,
        "payment_date": payment.payment_date.strftime("%d-%b-%Y, %I:%M %p"),
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "transaction_reference": payment.transaction_reference or "N/A",
        "notes": payment.notes or "Rent & Accommodation Maintenance",
        "tenant_id": payment.tenant_id,
        "tenant_name": tenant.full_name if tenant else "Guest",
        "tenant_phone": tenant.phone if tenant else "N/A",
        "room_number": room_info,
        "bed_number": bed_info,
        "pg_name": "Latha PG for Gents",
        "pg_name_kannada": "ಲತಾ ಪಿಜಿ - ಪುರುಷರಿಗೆ",
        "pg_contacts": "9353439703 / 9019870803",
        "pg_tagline": "Comfortable, Safe, Affordable • 2, 3, 4 Sharing"
    }


@router.get("/payments/{payment_id}/download-pdf")
def download_payment_receipt_pdf(payment_id: int, db: Session = Depends(get_db)):
    """Generate and download an official PDF receipt directly on any phone or desktop."""
    receipt_data = get_payment_receipt(payment_id=payment_id, db=db)
    pdf_bytes = generate_receipt_pdf_bytes(receipt_data)
    filename = f"Latha_PG_Receipt_{receipt_data['receipt_number']}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "no-cache"
        }
    )


@router.get("/payments/{payment_id}/view-pdf")
def view_payment_receipt_pdf(payment_id: int, db: Session = Depends(get_db)):
    """View official PDF receipt inline in the browser."""
    receipt_data = get_payment_receipt(payment_id=payment_id, db=db)
    pdf_bytes = generate_receipt_pdf_bytes(receipt_data)
    filename = f"Latha_PG_Receipt_{receipt_data['receipt_number']}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=\"{filename}\"",
            "Cache-Control": "no-cache"
        }
    )


@router.get("/tenants/{tenant_id}/dues", response_model=TenantDuesResponse)
def get_tenant_dues(tenant_id: int, db: Session = Depends(get_db)):
    """Calculate aggregate billed amount, total paid, and net pending dues for a tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    invoices = db.query(Invoice).filter(Invoice.tenant_id == tenant_id).all()
    total_billed = sum(inv.total_amount for inv in invoices)
    total_paid = sum(inv.paid_amount for inv in invoices)
    outstanding = total_billed - total_paid
    unpaid_count = sum(1 for inv in invoices if inv.status in ["UNPAID", "PARTIAL", "OVERDUE"])

    return TenantDuesResponse(
        tenant_id=tenant.id,
        tenant_name=tenant.full_name,
        total_billed=round(total_billed, 2),
        total_paid=round(total_paid, 2),
        outstanding_dues=round(outstanding if outstanding > 0 else 0.0, 2),
        unpaid_invoices_count=unpaid_count
    )
