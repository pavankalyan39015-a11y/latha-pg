from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class BedBase(BaseModel):
    bed_number: str
    status: str = "AVAILABLE"  # AVAILABLE, OCCUPIED, MAINTENANCE

class BedCreate(BedBase):
    pass

class BedUpdate(BaseModel):
    bed_number: Optional[str] = None
    status: Optional[str] = None

class BedResponse(BedBase):
    id: int
    room_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomBase(BaseModel):
    room_number: str
    floor: int = 1
    room_type: str = "Double"  # Single, Double, Triple, Four-Sharing
    has_ac: bool = False
    has_attached_bathroom: bool = True
    base_rent: float
    amenities: Optional[str] = "Wi-Fi, Wardrobe, Study Table"

class RoomCreate(RoomBase):
    total_beds: Optional[int] = None  # If provided, auto-generates beds (e.g. 101-A, 101-B)

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    has_ac: Optional[bool] = None
    has_attached_bathroom: Optional[bool] = None
    base_rent: Optional[float] = None
    amenities: Optional[str] = None

class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    beds: List[BedResponse] = []

    model_config = ConfigDict(from_attributes=True)
