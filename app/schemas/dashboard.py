from pydantic import BaseModel
from typing import Dict

class DashboardSummary(BaseModel):
    # Occupancy Metrics
    total_rooms: int
    total_beds: int
    occupied_beds: int
    available_beds: int
    maintenance_beds: int
    occupancy_rate_percent: float

    # Tenant Metrics
    active_tenants: int
    pending_kyc_count: int

    # Financial Metrics
    total_billed_amount: float
    total_collected_amount: float
    total_outstanding_dues: float

    # Complaints Metrics
    open_complaints: int
    urgent_complaints: int
    complaints_by_status: Dict[str, int]
