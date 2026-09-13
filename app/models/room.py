from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), unique=True, index=True, nullable=False)
    floor = Column(Integer, nullable=False, default=1)
    room_type = Column(String(50), nullable=False)  # Single, Double, Triple, Four-Sharing
    has_ac = Column(Boolean, default=False, nullable=False)
    has_attached_bathroom = Column(Boolean, default=True, nullable=False)
    base_rent = Column(Float, nullable=False)  # Monthly rent per bed
    amenities = Column(String(255), default="Wi-Fi, Wardrobe, Study Table")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    beds = relationship("Bed", back_populates="room", cascade="all, delete-orphan")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="room")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    bed_number = Column(String(50), nullable=False)  # e.g., "101-A"
    status = Column(String(50), default="AVAILABLE", nullable=False)  # AVAILABLE, OCCUPIED, MAINTENANCE
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="beds")
    tenant = relationship("Tenant", back_populates="bed", uselist=False)
