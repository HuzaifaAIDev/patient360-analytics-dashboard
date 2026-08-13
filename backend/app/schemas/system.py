"""Pydantic schemas for database connectivity and CORS status endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DatabaseStatus(BaseModel):
    """Live connectivity/health snapshot of the configured SQL database."""

    connected: bool
    driver: str
    database_name: str
    host: Optional[str] = None
    ssl_mode: Optional[str] = None
    total_records: int
    unique_patients: int
    message: str


class CorsOriginInfo(BaseModel):
    """A single row of the database-controlled `allowed_origins` table."""

    origin: str
    is_active: bool
    note: Optional[str] = None
    created_at: datetime
