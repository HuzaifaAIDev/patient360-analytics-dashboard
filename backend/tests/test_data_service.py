"""
Unit tests for the SQL-backed DataService.

These tests point the app at a throwaway SQLite file (never the real
configured database) so they're fully isolated and safe to run anywhere,
including CI, without needing PostgreSQL/MySQL installed.
"""
from __future__ import annotations

import os
from datetime import date

import pytest

from app.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.db.models import PatientVisit
from app.services.data_service import DataService

get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _fresh_schema():
    """Recreate a clean schema before every test, drop it after."""
    Base.metadata.create_all(bind=engine)
    yield
    with SessionLocal() as db:
        db.query(PatientVisit).delete()
        db.commit()


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db_file():
    """Remove the throwaway test SQLite file once the whole test session ends."""
    yield
    engine.dispose()
    test_db_path = "test_patient360.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def _insert(rows: list[dict]) -> None:
    with SessionLocal() as db:
        db.bulk_insert_mappings(PatientVisit, rows)
        db.commit()


SAMPLE_ROWS = [
    {
        "record_id": "rec1",
        "patient_name": "Ali Saleem",
        "visit_date": date(2024, 1, 10),
        "hospital": "National Hospital",
        "doctor": "Dr Ahmed",
        "city": "Karachi",
        "diseases": ["Diabetes", "Hypertension"],
        "claim_amount": 12000.0,
        "notes": None,
        "source_file": "seed",
    },
    {
        "record_id": "rec2",
        "patient_name": "Ali Saleem",
        "visit_date": date(2024, 3, 15),
        "hospital": "Shifa International",
        "doctor": "Dr Fatima Noor",
        "city": "Karachi",
        "diseases": ["Diabetes"],
        "claim_amount": 8000.0,
        "notes": "Follow-up",
        "source_file": "seed",
    },
    {
        "record_id": "rec3",
        "patient_name": "Sana Malik",
        "visit_date": date(2023, 11, 1),
        "hospital": "Shifa International",
        "doctor": "Dr Ahmed",
        "city": "Lahore",
        "diseases": ["Asthma"],
        "claim_amount": 5000.0,
        "notes": None,
        "source_file": "seed",
    },
]


def test_empty_database_returns_empty_dataframe():
    svc = DataService()
    assert svc.is_empty() is True
    assert svc.record_count() == 0
    assert svc.unique_patient_count() == 0
    df = svc.dataframe
    assert df.empty
    assert list(df.columns) == [
        "record_id", "patient_name", "visit_date", "hospital", "doctor",
        "city", "diseases", "claim_amount", "notes", "source_file",
    ]


def test_dataframe_reflects_inserted_rows():
    _insert(SAMPLE_ROWS)
    svc = DataService()

    assert svc.is_empty() is False
    assert svc.record_count() == 3
    assert svc.unique_patient_count() == 2

    df = svc.dataframe
    assert len(df) == 3
    assert set(df["patient_name"]) == {"Ali Saleem", "Sana Malik"}


def test_diseases_column_round_trips_as_list():
    _insert(SAMPLE_ROWS)
    df = DataService().dataframe
    row = df[df["record_id"] == "rec1"].iloc[0]
    assert isinstance(row["diseases"], list)
    assert row["diseases"] == ["Diabetes", "Hypertension"]


def test_filtering_by_patient_matches_original_json_pipeline_shape():
    """
    The rest of the app (routes/analytics) filters the full DataFrame with
    plain pandas — e.g. df[df.patient_name == name] — exactly like it did
    when the DataFrame came from JSON files. This confirms that contract
    still holds now that the DataFrame is populated from SQL instead.
    """
    _insert(SAMPLE_ROWS)
    df = DataService().dataframe
    ali_df = df[df["patient_name"] == "Ali Saleem"]
    assert len(ali_df) == 2
    assert set(ali_df["hospital"]) == {"National Hospital", "Shifa International"}


def test_record_ids_are_unique_and_used_for_dedup():
    _insert(SAMPLE_ROWS)
    df = DataService().dataframe
    assert df["record_id"].is_unique
