from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BookingInquiryBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    room_type: str = "Standard Room"
    sharing_preference: str = "2 Sharing"  # 2 Sharing, 3 Sharing, 4 Sharing
    preferred_move_in_date: str
    notes: Optional[str] = None

class BookingInquiryCreate(BookingInquiryBase):
    pass

class BookingInquiryUpdate(BaseModel):
    status: Optional[str] = None  # NEW, CONTACTED, VISITED, BOOKED, CANCELLED
    notes: Optional[str] = None

class BookingInquiryResponse(BookingInquiryBase):
    id: int
    reference_code: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConvertToTenantRequest(BaseModel):
    bed_id: int
    security_deposit: float = 3000.0
    rent_amount: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    permanent_address: Optional[str] = None
    occupation: Optional[str] = None
    id_proof_type: str = "Aadhaar"
    id_proof_number: Optional[str] = None
