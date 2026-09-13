from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    permanent_address = Column(Text, nullable=True)
    occupation = Column(String(100), nullable=True)  # e.g., "Software Engineer @ TechCorp", "Student"

    # KYC Info
    id_proof_type = Column(String(50), default="Aadhaar")  # Aadhaar, Passport, Driving License, Voter ID
    id_proof_number = Column(String(100), nullable=True)
    kyc_status = Column(String(20), default="PENDING", nullable=False)  # PENDING, VERIFIED, REJECTED

    # Stay Details
    check_in_date = Column(Date, default=date.today, nullable=False)
    check_out_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    security_deposit = Column(Float, default=0.0, nullable=False)

    # Bed allocation
    bed_id = Column(Integer, ForeignKey("beds.id"), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bed = relationship("Bed", back_populates="tenant")
    documents = relationship("TenantDocument", back_populates="tenant", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="tenant", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tenant", cascade="all, delete-orphan")
    maintenance_tickets = relationship("MaintenanceTicket", back_populates="tenant")
    meal_attendances = relationship("MealAttendance", back_populates="tenant", cascade="all, delete-orphan")


class TenantDocument(Base):
    __tablename__ = "tenant_documents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    document_name = Column(String(100), nullable=False)  # e.g. "Aadhaar Card Front", "College ID"
    document_path_or_url = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
