from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.models.maintenance import MaintenanceTicket
from app.schemas.maintenance import (
    MaintenanceTicketResponse, MaintenanceTicketCreate, MaintenanceTicketUpdate
)

router = APIRouter(prefix="/complaints", tags=["Maintenance & Complaints"])

@router.get("", response_model=List[MaintenanceTicketResponse])
def list_complaints(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)"),
    category: Optional[str] = Query(None, description="Filter by category (PLUMBING, ELECTRICAL, WIFI, CLEANING, etc.)"),
    priority: Optional[str] = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH, URGENT)"),
    tenant_id: Optional[int] = Query(None, description="Filter by reporting tenant"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    db: Session = Depends(get_db)
):
    """List maintenance tickets and complaints filed by tenants or staff."""
    query = db.query(MaintenanceTicket)
    if status:
        query = query.filter(MaintenanceTicket.status == status.upper())
    if category:
        query = query.filter(MaintenanceTicket.category == category.upper())
    if priority:
        query = query.filter(MaintenanceTicket.priority == priority.upper())
    if tenant_id:
        query = query.filter(MaintenanceTicket.tenant_id == tenant_id)
    if room_id:
        query = query.filter(MaintenanceTicket.room_id == room_id)
    return query.order_by(MaintenanceTicket.reported_at.desc()).all()


@router.post("", response_model=MaintenanceTicketResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(ticket_in: MaintenanceTicketCreate, db: Session = Depends(get_db)):
    """File a new complaint or maintenance request."""
    ticket_num = f"TKT-{datetime.utcnow().strftime('%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    ticket = MaintenanceTicket(
        ticket_number=ticket_num,
        tenant_id=ticket_in.tenant_id,
        room_id=ticket_in.room_id,
        category=ticket_in.category.upper(),
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority.upper(),
        status="OPEN",
        reported_at=datetime.utcnow()
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=MaintenanceTicketResponse)
def get_complaint(ticket_id: int, db: Session = Depends(get_db)):
    """Fetch complaint details by ID."""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint ticket not found.")
    return ticket


@router.patch("/{ticket_id}", response_model=MaintenanceTicketResponse)
def update_complaint(ticket_id: int, ticket_in: MaintenanceTicketUpdate, db: Session = Depends(get_db)):
    """Update complaint status (e.g. mark RESOLVED with resolution notes) or priority."""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint ticket not found.")

    if ticket_in.priority:
        ticket.priority = ticket_in.priority.upper()

    if ticket_in.status:
        ticket.status = ticket_in.status.upper()
        if ticket.status in ["RESOLVED", "CLOSED"] and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()

    if ticket_in.resolution_notes:
        ticket.resolution_notes = ticket_in.resolution_notes

    db.commit()
    db.refresh(ticket)
    return ticket
