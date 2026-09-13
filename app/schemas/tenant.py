from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional
from datetime import date, datetime

class TenantDocumentBase(BaseModel):
    document_name: str
    document_path_or_url: str

class TenantDocumentCreate(TenantDocumentBase):
    pass

class TenantDocumentResponse(TenantDocumentBase):
    id: int
    tenant_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    permanent_address: Optional[str] = None
    occupation: Optional[str] = None

    id_proof_type: str = "Aadhaar"
    id_proof_number: Optional[str] = None
    security_deposit: float = 0.0

class TenantCreate(TenantBase):
    check_in_date: Optional[date] = None
    bed_id: Optional[int] = None  # Assign bed directly during onboarding

class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    permanent_address: Optional[str] = None
    occupation: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    kyc_status: Optional[str] = None  # PENDING, VERIFIED, REJECTED
    bed_id: Optional[int] = None
    is_active: Optional[bool] = None

class BedSummary(BaseModel):
    id: int
    bed_number: str
    room_id: int
    model_config = ConfigDict(from_attributes=True)

class TenantResponse(TenantBase):
    id: int
    kyc_status: str
    check_in_date: date
    check_out_date: Optional[date] = None
    is_active: bool
    bed_id: Optional[int] = None
    bed: Optional[BedSummary] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TenantDetailResponse(TenantResponse):
    documents: List[TenantDocumentResponse] = []
    model_config = ConfigDict(from_attributes=True)

class TenantCheckout(BaseModel):
    check_out_date: Optional[date] = None
    refund_deposit_amount: Optional[float] = None
    remarks: Optional[str] = None
