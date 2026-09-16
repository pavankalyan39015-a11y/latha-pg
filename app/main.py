from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
import app.models  # Ensures all models are registered on Base.metadata
from app.routers import (
    rooms_router,
    tenants_router,
    billing_router,
    maintenance_router,
    meals_router,
    dashboard_router,
    booking_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
api_v1_prefix = "/api/v1"
app.include_router(dashboard_router, prefix=api_v1_prefix)
app.include_router(rooms_router, prefix=api_v1_prefix)
app.include_router(tenants_router, prefix=api_v1_prefix)
app.include_router(billing_router, prefix=api_v1_prefix)
app.include_router(maintenance_router, prefix=api_v1_prefix)
app.include_router(meals_router, prefix=api_v1_prefix)
app.include_router(booking_router, prefix=api_v1_prefix)


# Mount Static Dashboard SPA
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")

@app.get("/", include_in_schema=False)
def root():
    """Redirect root to the modern web dashboard."""
    return RedirectResponse(url="/dashboard")

@app.get("/health", tags=["Health & Info"])
def health_check():
    """System health check endpoint."""
    return {"status": "healthy"}

