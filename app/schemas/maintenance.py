from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MaintenanceTicketBase(BaseModel):
    category: str  # PLUMBING, ELECTRICAL, WIFI, CLEANING, APPLIANCE, OTHER
    title: str
    description: str
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, URGENT
    tenant_id: Optional[int] = None
    room_id: Optional[int] = None

class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass

class MaintenanceTicketUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    resolution_notes: Optional[str] = None

class MaintenanceTicketResponse(MaintenanceTicketBase):
    id: int
    ticket_number: str
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
