from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class MealMenu(Base):
    __tablename__ = "meal_menus"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String(20), nullable=False)  # Monday, Tuesday, ... Sunday
    meal_type = Column(String(20), nullable=False)  # BREAKFAST, LUNCH, DINNER
    items = Column(Text, nullable=False)  # e.g., "Poha, boiled eggs, tea/coffee"
    is_special = Column(Boolean, default=False, nullable=False)


class MealAttendance(Base):
    __tablename__ = "meal_attendances"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    meal_type = Column(String(20), nullable=False)  # BREAKFAST, LUNCH, DINNER
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    is_attending = Column(Boolean, default=True, nullable=False)
    wants_packed_meal = Column(Boolean, default=False, nullable=False)
    feedback = Column(String(255), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="meal_attendances")
