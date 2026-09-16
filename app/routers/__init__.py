from app.routers.rooms import router as rooms_router
from app.routers.tenants import router as tenants_router
from app.routers.billing import router as billing_router
from app.routers.maintenance import router as maintenance_router
from app.routers.meals import router as meals_router
from app.routers.dashboard import router as dashboard_router
from app.routers.booking import router as booking_router

__all__ = [
    "rooms_router",
    "tenants_router",
    "billing_router",
    "maintenance_router",
    "meals_router",
    "dashboard_router",
    "booking_router",
]

