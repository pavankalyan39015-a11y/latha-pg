from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    billing_month = Column(String(20), nullable=False)  # e.g., "2026-09"
    due_date = Column(Date, nullable=False)

    rent_amount = Column(Float, nullable=False)
    utility_charges = Column(Float, default=0.0, nullable=False)  # Electricity, Wi-Fi, laundry, etc.
    penalty_charges = Column(Float, default=0.0, nullable=False)  # Late fees
    discount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0, nullable=False)

    status = Column(String(20), default="UNPAID", nullable=False)  # UNPAID, PARTIAL, PAID, OVERDUE
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="UPI", nullable=False)  # UPI, CASH, BANK_TRANSFER, CARD
    transaction_reference = Column(String(100), nullable=True)  # UPI Ref / UTR / Cheque No.
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
