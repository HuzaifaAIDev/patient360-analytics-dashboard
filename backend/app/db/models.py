"""ORM models for the SQL-backed patient dataset."""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.session import Base


class PatientVisit(Base):
    """
    A single patient visit record.

    This is the SQL equivalent of the JSON objects the app used to ingest
    from uploaded files — same fields, now the row of a real, credentialed,
    access-controlled database table instead of an in-memory/JSON structure.
    """

    __tablename__ = "patient_visits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    visit_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    hospital: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    doctor: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    diseases: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    claim_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        # Speeds up the two most common access patterns: "find this patient's
        # visits" (search/dashboard) and "visits in date order" (timeline).
        Index("ix_patient_visits_patient_date", "patient_name", "visit_date"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<PatientVisit id={self.id} patient={self.patient_name!r} date={self.visit_date}>"


class AllowedOrigin(Base):
    """
    A single CORS-allowed origin, e.g. "http://localhost:5173" or
    "https://app.yourcompany.com".

    This is what makes CORS a database-controlled setting rather than a
    static `.env` value: the app reads this table (through a short-lived
    in-memory cache, see `app/services/cors_service.py`) to decide which
    origins may call the API, and picks up changes without a redeploy —
    add, disable, or remove a row and it takes effect within one cache
    refresh window instead of requiring a restart.
    """

    __tablename__ = "allowed_origins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<AllowedOrigin id={self.id} origin={self.origin!r} active={self.is_active}>"
