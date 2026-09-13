from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class PaymentBase(BaseModel):
    amount: float
    payment_method: str = "UPI"  # UPI, CASH, BANK_TRANSFER, CARD
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    tenant_id: int
    invoice_id: Optional[int] = None
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    id: int
    receipt_number: str
    invoice_id: Optional[int] = None
    tenant_id: int
    payment_date: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    tenant_id: int
    billing_month: str  # YYYY-MM
    due_date: date
    rent_amount: float
    utility_charges: float = 0.0
    penalty_charges: float = 0.0
    discount: float = 0.0
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    rent_amount: Optional[float] = None
    utility_charges: Optional[float] = None
    penalty_charges: Optional[float] = None
    discount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    tenant_id: int
    billing_month: str
    due_date: date
    rent_amount: float
    utility_charges: float
    penalty_charges: float
    discount: float
    total_amount: float
    paid_amount: float
    status: str  # UNPAID, PARTIAL, PAID, OVERDUE
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvoiceDetailResponse(InvoiceResponse):
    payments: List[PaymentResponse] = []
    model_config = ConfigDict(from_attributes=True)

class TenantDuesResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    total_billed: float
    total_paid: float
    outstanding_dues: float
    unpaid_invoices_count: int
