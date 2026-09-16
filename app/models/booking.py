from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
import random
from app.database import Base

class BookingInquiry(Base):
    __tablename__ = "booking_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    reference_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    room_type = Column(String(50), nullable=False)
    sharing_preference = Column(String(50), nullable=False)
    preferred_move_in_date = Column(String(50), nullable=False)
    status = Column(String(50), default="NEW", nullable=False)  # NEW, CONTACTED, VISITED, BOOKED, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_reference_code():
        return f"LATHA-BKG-{random.randint(1000, 9999)}"
