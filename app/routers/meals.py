from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.meal import MealMenu, MealAttendance
from app.models.tenant import Tenant
from app.schemas.meal import (
    MealMenuResponse, MealMenuCreate, MealAttendanceResponse,
    MealAttendanceCreate, DailyMealHeadcount
)

router = APIRouter(prefix="/meals", tags=["Mess & Meal Management"])

@router.get("/menu", response_model=List[MealMenuResponse])
def get_meal_menu(
    day: Optional[str] = Query(None, description="Filter by day of week (e.g., Monday, Sunday)"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type (BREAKFAST, LUNCH, DINNER)"),
    db: Session = Depends(get_db)
):
    """Retrieve the mess menu schedule."""
    query = db.query(MealMenu)
    if day:
        query = query.filter(MealMenu.day_of_week.ilike(day))
    if meal_type:
        query = query.filter(MealMenu.meal_type == meal_type.upper())
    return query.all()


@router.post("/menu", response_model=MealMenuResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_menu_item(menu_in: MealMenuCreate, db: Session = Depends(get_db)):
    """Add or update a meal menu item for a specific day and meal type."""
    day_clean = menu_in.day_of_week.capitalize()
    meal_clean = menu_in.meal_type.upper()

    existing = db.query(MealMenu).filter(
        MealMenu.day_of_week == day_clean,
        MealMenu.meal_type == meal_clean
    ).first()

    if existing:
        existing.items = menu_in.items
        existing.is_special = menu_in.is_special
        db.commit()
        db.refresh(existing)
        return existing

    item = MealMenu(
        day_of_week=day_clean,
        meal_type=meal_clean,
        items=menu_in.items,
        is_special=menu_in.is_special
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/attendance", response_model=MealAttendanceResponse, status_code=status.HTTP_201_CREATED)
def log_meal_attendance(attendance_in: MealAttendanceCreate, db: Session = Depends(get_db)):
    """Record tenant meal attendance, opt-out, or packed lunch request for a specific date."""
    tenant = db.query(Tenant).filter(Tenant.id == attendance_in.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    meal_type_clean = attendance_in.meal_type.upper()

    existing = db.query(MealAttendance).filter(
        MealAttendance.tenant_id == attendance_in.tenant_id,
        MealAttendance.date == attendance_in.date,
        MealAttendance.meal_type == meal_type_clean
    ).first()

    if existing:
        existing.is_attending = attendance_in.is_attending
        existing.wants_packed_meal = attendance_in.wants_packed_meal
        existing.feedback = attendance_in.feedback
        db.commit()
        db.refresh(existing)
        return existing

    attendance = MealAttendance(
        date=attendance_in.date,
        meal_type=meal_type_clean,
        tenant_id=attendance_in.tenant_id,
        is_attending=attendance_in.is_attending,
        wants_packed_meal=attendance_in.wants_packed_meal,
        feedback=attendance_in.feedback
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/headcount", response_model=DailyMealHeadcount)
def get_daily_meal_headcount(
    target_date: date = Query(default_factory=date.today, description="Date for headcount check"),
    meal_type: str = Query("DINNER", description="Meal type (BREAKFAST, LUNCH, DINNER)"),
    db: Session = Depends(get_db)
):
    """Get the estimated headcount for kitchen staff: attending, packed lunch, and opted-out tenants."""
    meal_type_clean = meal_type.upper()
    active_tenants_count = db.query(Tenant).filter(Tenant.is_active == True).count()

    attendances = db.query(MealAttendance).filter(
        MealAttendance.date == target_date,
        MealAttendance.meal_type == meal_type_clean
    ).all()

    attending_count = 0
    packed_meal_count = 0
    opt_out_count = 0

    logged_tenants = set()
    for att in attendances:
        logged_tenants.add(att.tenant_id)
        if att.is_attending:
            attending_count += 1
            if att.wants_packed_meal:
                packed_meal_count += 1
        else:
            opt_out_count += 1

    # Active tenants who haven't opted out are assumed attending by default
    unlogged_active = max(0, active_tenants_count - len(logged_tenants))
    total_attending = attending_count + unlogged_active

    return DailyMealHeadcount(
        date=target_date,
        meal_type=meal_type_clean,
        attending_count=total_attending,
        packed_meal_count=packed_meal_count,
        opt_out_count=opt_out_count
    )
