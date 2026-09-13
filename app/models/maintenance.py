from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)

    category = Column(String(50), nullable=False)  # PLUMBING, ELECTRICAL, WIFI, CLEANING, APPLIANCE, OTHER
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED

    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="maintenance_tickets")
    room = relationship("Room", back_populates="maintenance_tickets")
