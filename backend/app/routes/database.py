"""Database connectivity, status, and CORS-origin visibility endpoints."""
from __future__ import annotations

from typing import List
from urllib.parse import urlparse

from fastapi import APIRouter
from sqlalchemy import select

from app.config import get_settings
from app.db.models import AllowedOrigin
from app.db.session import SessionLocal, check_database_connection
from app.schemas.system import CorsOriginInfo, DatabaseStatus
from app.services.data_service import data_service

router = APIRouter(prefix="/api/database", tags=["Database"])


@router.get("/status", response_model=DatabaseStatus)
async def database_status() -> DatabaseStatus:
    """
    Live health check for the configured SQL database.

    Reports whether the connection succeeds, which driver/database it's
    talking to, and current record counts — without ever exposing the
    username or password from the connection string.
    """
    settings = get_settings()
    connected, message = check_database_connection()

    parsed = urlparse(settings.sqlalchemy_database_url)
    host = parsed.hostname if parsed.hostname else None
    database_name = (parsed.path or "").lstrip("/") or settings.db_name

    total_records = data_service.record_count() if connected else 0
    unique_patients = data_service.unique_patient_count() if connected else 0

    return DatabaseStatus(
        connected=connected,
        driver=settings.resolved_driver_name,
        database_name=database_name,
        host=host,
        ssl_mode=settings.db_ssl_mode if not settings.is_sqlite else None,
        total_records=total_records,
        unique_patients=unique_patients,
        message=message,
    )


@router.get("/cors-origins", response_model=List[CorsOriginInfo])
async def list_cors_origins() -> List[CorsOriginInfo]:
    """
    Read-only visibility into which frontend origins are currently allowed
    to call this API. The list itself lives in the `allowed_origins` table —
    add/disable/remove rows there (directly, or via the seed script) to
    change it; this endpoint deliberately has no write counterpart, since an
    unauthenticated POST/PUT here would let anyone grant their own origin
    access.
    """
    connected, _ = check_database_connection()
    if not connected:
        return []
    with SessionLocal() as db:
        rows = db.execute(
            select(AllowedOrigin).order_by(AllowedOrigin.created_at.asc())
        ).scalars().all()
    return [
        CorsOriginInfo(origin=r.origin, is_active=r.is_active, note=r.note, created_at=r.created_at)
        for r in rows
    ]
