"""Unit tests for the analytics layer."""
from __future__ import annotations

import pandas as pd
import pytest

from app.analytics import global_analytics as ga
from app.analytics import patient_analytics as pa

SAMPLE_ROWS = [
    {
        "record_id": "1",
        "patient_name": "Ali Saleem",
        "visit_date": "2024-01-10",
        "hospital": "National Hospital",
        "doctor": "Dr Ahmed",
        "city": "Karachi",
        "diseases": ["Diabetes", "Hypertension"],
        "claim_amount": 12000,
        "notes": None,
        "source_file": "f1.json",
    },
    {
        "record_id": "2",
        "patient_name": "Ali Saleem",
        "visit_date": "2024-03-15",
        "hospital": "National Hospital",
        "doctor": "Dr Fatima Noor",
        "city": "Karachi",
        "diseases": ["Diabetes"],
        "claim_amount": 8000,
        "notes": "Follow-up",
        "source_file": "f1.json",
    },
    {
        "record_id": "3",
        "patient_name": "Ali Saleem",
        "visit_date": "2023-11-01",
        "hospital": "Shifa International",
        "doctor": "Dr Ahmed",
        "city": "Lahore",
        "diseases": ["Asthma"],
        "claim_amount": 5000,
        "notes": None,
        "source_file": "f2.json",
    },
]


@pytest.fixture
def df():
    return pd.DataFrame(SAMPLE_ROWS)


def test_compute_patient_stats(df):
    stats = pa.compute_patient_stats("Ali Saleem", df)
    assert stats.total_records == 3
    assert stats.first_visit.isoformat() == "2023-11-01"
    assert stats.last_visit.isoformat() == "2024-03-15"
    assert stats.total_claimed_amount == 25000
    assert stats.average_claim == pytest.approx(8333.33, rel=1e-2)
    assert "National Hospital" in stats.hospitals_visited
    assert "Shifa International" in stats.hospitals_visited


def test_compute_patient_stats_empty():
    empty = pd.DataFrame(columns=SAMPLE_ROWS[0].keys())
    stats = pa.compute_patient_stats("Nobody", empty)
    assert stats.total_records == 0
    assert stats.first_visit is None


def test_hospital_breakdown(df):
    items = pa.hospital_breakdown(df)
    labels = {i.label: i.count for i in items}
    assert labels["National Hospital"] == 2
    assert labels["Shifa International"] == 1


def test_disease_breakdown_flattens_arrays(df):
    result = pa.disease_breakdown(df, recurring_threshold=2)
    freq = {f["label"]: f["count"] for f in result["frequencies"]}
    assert freq["Diabetes"] == 2
    assert freq["Hypertension"] == 1
    assert freq["Asthma"] == 1
    assert "Diabetes" in result["recurring_diseases"]
    assert "Asthma" not in result["recurring_diseases"]


def test_disease_breakdown_empty():
    empty = pd.DataFrame(columns=SAMPLE_ROWS[0].keys())
    result = pa.disease_breakdown(empty)
    assert result["frequencies"] == []
    assert result["recurring_diseases"] == []


def test_timeline_cards_sorting(df):
    desc = pa.timeline_cards(df, order="desc")
    asc = pa.timeline_cards(df, order="asc")
    assert desc[0]["visit_date"].startswith("2024-03")
    assert asc[0]["visit_date"].startswith("2023-11")


def test_claims_per_hospital(df):
    result = pa.claims_per_hospital(df)
    by_hospital = {r["hospital"]: r["total_claim"] for r in result}
    assert by_hospital["National Hospital"] == 20000
    assert by_hospital["Shifa International"] == 5000


def test_dataset_overview(df):
    overview = ga.dataset_overview(df)
    assert overview["total_records"] == 3
    assert overview["unique_patients"] == 1
    assert overview["total_claimed_amount"] == 25000


def test_dataset_overview_empty():
    empty = pd.DataFrame(columns=SAMPLE_ROWS[0].keys())
    overview = ga.dataset_overview(empty)
    assert overview["total_records"] == 0
    assert overview["hospital_breakdown"] == []
