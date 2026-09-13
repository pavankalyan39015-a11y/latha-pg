from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.room import Room, Bed
from app.models.tenant import Tenant
from app.models.billing import Invoice, Payment
from app.models.maintenance import MaintenanceTicket
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve executive real-time overview: occupancy, pending dues, collections, and complaints."""
    # Room & Bed stats
    total_rooms = db.query(Room).count()
    total_beds = db.query(Bed).count()
    occupied_beds = db.query(Bed).filter(Bed.status == "OCCUPIED").count()
    available_beds = db.query(Bed).filter(Bed.status == "AVAILABLE").count()
    maintenance_beds = db.query(Bed).filter(Bed.status == "MAINTENANCE").count()
    occupancy_rate = (occupied_beds / total_beds * 100.0) if total_beds > 0 else 0.0

    # Tenant stats
    active_tenants = db.query(Tenant).filter(Tenant.is_active == True).count()
    pending_kyc = db.query(Tenant).filter(Tenant.kyc_status == "PENDING", Tenant.is_active == True).count()

    # Billing & Financials
    total_billed = db.query(func.coalesce(func.sum(Invoice.total_amount), 0.0)).scalar()
    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar()
    total_dues = max(0.0, float(total_billed) - float(total_collected))

    # Maintenance tickets
    open_tickets = db.query(MaintenanceTicket).filter(MaintenanceTicket.status.in_(["OPEN", "IN_PROGRESS"])).count()
    urgent_tickets = db.query(MaintenanceTicket).filter(
        MaintenanceTicket.priority == "URGENT",
        MaintenanceTicket.status.in_(["OPEN", "IN_PROGRESS"])
    ).count()

    # Breakdown by status
    statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
    complaints_by_status = {}
    for st in statuses:
        complaints_by_status[st] = db.query(MaintenanceTicket).filter(MaintenanceTicket.status == st).count()

    return DashboardSummary(
        total_rooms=total_rooms,
        total_beds=total_beds,
        occupied_beds=occupied_beds,
        available_beds=available_beds,
        maintenance_beds=maintenance_beds,
        occupancy_rate_percent=round(occupancy_rate, 1),
        active_tenants=active_tenants,
        pending_kyc_count=pending_kyc,
        total_billed_amount=round(float(total_billed), 2),
        total_collected_amount=round(float(total_collected), 2),
        total_outstanding_dues=round(float(total_dues), 2),
        open_complaints=open_tickets,
        urgent_complaints=urgent_tickets,
        complaints_by_status=complaints_by_status
    )
