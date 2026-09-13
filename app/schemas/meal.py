from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class MealMenuBase(BaseModel):
    day_of_week: str  # Monday, Tuesday, ... Sunday
    meal_type: str  # BREAKFAST, LUNCH, DINNER
    items: str
    is_special: bool = False

class MealMenuCreate(MealMenuBase):
    pass

class MealMenuResponse(MealMenuBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MealAttendanceBase(BaseModel):
    date: date
    meal_type: str  # BREAKFAST, LUNCH, DINNER
    tenant_id: int
    is_attending: bool = True
    wants_packed_meal: bool = False
    feedback: Optional[str] = None

class MealAttendanceCreate(MealAttendanceBase):
    pass

class MealAttendanceResponse(MealAttendanceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DailyMealHeadcount(BaseModel):
    date: date
    meal_type: str
    attending_count: int
    packed_meal_count: int
    opt_out_count: int
