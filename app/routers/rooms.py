from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.room import Room, Bed
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate, BedResponse, BedCreate, BedUpdate

router = APIRouter(prefix="/rooms", tags=["Rooms & Beds"])

@router.get("", response_model=List[RoomResponse])
def list_rooms(
    floor: Optional[int] = Query(None, description="Filter by floor number"),
    room_type: Optional[str] = Query(None, description="Filter by room type (e.g., Single, Double, Triple)"),
    has_ac: Optional[bool] = Query(None, description="Filter by AC availability"),
    db: Session = Depends(get_db)
):
    """Retrieve all PG rooms with their bed statuses and amenities."""
    query = db.query(Room)
    if floor is not None:
        query = query.filter(Room.floor == floor)
    if room_type:
        query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
    if has_ac is not None:
        query = query.filter(Room.has_ac == has_ac)
    return query.all()


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room_in: RoomCreate, db: Session = Depends(get_db)):
    """Create a new room in the PG. If total_beds is provided, automatically generates bed slots."""
    existing = db.query(Room).filter(Room.room_number == room_in.room_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room with number '{room_in.room_number}' already exists."
        )

    room = Room(
        room_number=room_in.room_number,
        floor=room_in.floor,
        room_type=room_in.room_type,
        has_ac=room_in.has_ac,
        has_attached_bathroom=room_in.has_attached_bathroom,
        base_rent=room_in.base_rent,
        amenities=room_in.amenities,
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # Auto-generate beds if requested
    bed_count = room_in.total_beds
    if not bed_count:
        # Default by type
        type_lower = room_in.room_type.lower()
        if "single" in type_lower:
            bed_count = 1
        elif "double" in type_lower:
            bed_count = 2
        elif "triple" in type_lower:
            bed_count = 3
        elif "four" in type_lower:
            bed_count = 4
        else:
            bed_count = 1

    for i in range(bed_count):
        bed_letter = chr(65 + i)  # A, B, C, D...
        bed = Bed(
            room_id=room.id,
            bed_number=f"{room.room_number}-{bed_letter}",
            status="AVAILABLE"
        )
        db.add(bed)

    db.commit()
    db.refresh(room)
    return room


@router.get("/beds/available", response_model=List[BedResponse], tags=["Rooms & Beds"])
def list_available_beds(db: Session = Depends(get_db)):
    """List all vacant beds available for tenant allocation across all rooms."""
    return db.query(Bed).filter(Bed.status == "AVAILABLE").all()


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Fetch single room details by ID."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room_in: RoomUpdate, db: Session = Depends(get_db)):
    """Update room attributes such as base rent, AC, amenities, etc."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    update_data = room_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """Delete a room. Disallowed if any beds in the room are currently occupied by active tenants."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    occupied = db.query(Bed).filter(Bed.room_id == room_id, Bed.status == "OCCUPIED").first()
    if occupied:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete room because it currently has occupied beds. Check out tenants first."
        )

    db.delete(room)
    db.commit()
    return None


@router.post("/{room_id}/beds", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
def add_bed_to_room(room_id: int, bed_in: BedCreate, db: Session = Depends(get_db)):
    """Add an extra bed slot to an existing room."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    bed = Bed(
        room_id=room.id,
        bed_number=bed_in.bed_number,
        status=bed_in.status
    )
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


@router.patch("/beds/{bed_id}/status", response_model=BedResponse, tags=["Rooms & Beds"])
def update_bed_status(bed_id: int, bed_in: BedUpdate, db: Session = Depends(get_db)):
    """Update bed occupancy status (AVAILABLE, OCCUPIED, MAINTENANCE)."""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bed not found.")

    if bed_in.status:
        bed.status = bed_in.status.upper()
    if bed_in.bed_number:
        bed.bed_number = bed_in.bed_number

    db.commit()
    db.refresh(bed)
    return bed


@router.delete("/beds/{bed_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Rooms & Beds"])
def delete_bed(bed_id: int, db: Session = Depends(get_db)):
    """Delete an unoccupied bed slot from a room."""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bed not found.")

    if bed.status == "OCCUPIED" or bed.tenant is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete bed '{bed.bed_number}' because it is currently occupied. Check out tenant first."
        )

    db.delete(bed)
    db.commit()
    return None

