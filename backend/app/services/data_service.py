"""
Dataset service — SQL-backed.

Every patient record lives in the `patient_visits` table of whichever
database is configured in `.env` (SQLite for local/demo use, PostgreSQL or
MySQL in production — see `app/config/settings.py`). This service is the
only place in the app that talks to that table; everything else (routes,
analytics, exports) works against the pandas DataFrame this returns, so the
rest of the codebase is completely unaware of where the data physically
lives.

All queries go through SQLAlchemy, which parameterizes every value —
patient names, search terms, etc. are never interpolated into raw SQL
strings, which is what prevents SQL injection.
"""
from __future__ import annotations

import json
import logging
import threading

import pandas as pd
from sqlalchemy import func, select

from app.db.models import PatientVisit
from app.db.session import SessionLocal

logger = logging.getLogger("patient360.data_service")

DATASET_COLUMNS = [
    "record_id",
    "patient_name",
    "visit_date",
    "hospital",
    "doctor",
    "city",
    "diseases",
    "claim_amount",
    "notes",
    "source_file",
]


class DataService:
    """Thin, thread-safe query layer over the `patient_visits` SQL table."""

    def __init__(self) -> None:
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Read access
    # ------------------------------------------------------------------
    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Load the full patient_visits table into a pandas DataFrame.

        Every existing analytics/search function in this app operates on a
        DataFrame with exactly these columns, so switching the underlying
        storage from JSON files to SQL required no changes anywhere except
        how this one DataFrame gets populated.
        """
        with self._lock:
            with SessionLocal() as db:
                stmt = select(
                    PatientVisit.record_id,
                    PatientVisit.patient_name,
                    PatientVisit.visit_date,
                    PatientVisit.hospital,
                    PatientVisit.doctor,
                    PatientVisit.city,
                    PatientVisit.diseases,
                    PatientVisit.claim_amount,
                    PatientVisit.notes,
                    PatientVisit.source_file,
                )
                rows = db.execute(stmt).all()

        if not rows:
            return pd.DataFrame(columns=DATASET_COLUMNS)

        df = pd.DataFrame(rows, columns=DATASET_COLUMNS)

        # SQLite's JSON type round-trips through SQLAlchemy's ORM layer fine,
        # but defensively normalize here too in case a raw/legacy row stored
        # diseases as a JSON *string* rather than a native list.
        def _normalize_diseases(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    return parsed if isinstance(parsed, list) else [value]
                except json.JSONDecodeError:
                    return [value]
            return []

        df["diseases"] = df["diseases"].apply(_normalize_diseases)
        return df

    def is_empty(self) -> bool:
        return self.record_count() == 0

    def record_count(self) -> int:
        with SessionLocal() as db:
            return db.execute(select(func.count()).select_from(PatientVisit)).scalar_one()

    def unique_patient_count(self) -> int:
        with SessionLocal() as db:
            return db.execute(select(func.count(func.distinct(PatientVisit.patient_name)))).scalar_one()


# Module-level singleton used across the app (simple dependency-injection point)
data_service = DataService()
