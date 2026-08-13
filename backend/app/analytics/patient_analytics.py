"""
Analytics functions for a single patient's records.

All functions take a pandas DataFrame already filtered to one patient and
return plain Python structures ready to be wrapped in Pydantic schemas or
serialized to JSON.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

import pandas as pd

from app.schemas.patient import CountItem, PatientSummaryStats


def compute_patient_stats(patient_name: str, df: pd.DataFrame) -> PatientSummaryStats:
    """Compute headline statistics for a single patient's visit history."""
    if df.empty:
        return PatientSummaryStats(
            patient_name=patient_name,
            total_records=0,
            total_visits=0,
            first_visit=None,
            last_visit=None,
            hospitals_visited=[],
            doctors_consulted=[],
            cities_visited=[],
            average_claim=None,
            highest_claim=None,
            lowest_claim=None,
            total_claimed_amount=None,
        )

    dates = pd.to_datetime(df["visit_date"], errors="coerce").dropna()
    claims = pd.to_numeric(df["claim_amount"], errors="coerce").dropna()

    return PatientSummaryStats(
        patient_name=patient_name,
        total_records=len(df),
        total_visits=int(df[["visit_date", "hospital", "doctor"]].drop_duplicates().shape[0]),
        first_visit=dates.min().date() if not dates.empty else None,
        last_visit=dates.max().date() if not dates.empty else None,
        hospitals_visited=sorted(df["hospital"].dropna().unique().tolist()),
        doctors_consulted=sorted(df["doctor"].dropna().unique().tolist()),
        cities_visited=sorted(df["city"].dropna().unique().tolist()),
        average_claim=round(float(claims.mean()), 2) if not claims.empty else None,
        highest_claim=round(float(claims.max()), 2) if not claims.empty else None,
        lowest_claim=round(float(claims.min()), 2) if not claims.empty else None,
        total_claimed_amount=round(float(claims.sum()), 2) if not claims.empty else None,
    )


def _counter_to_items(counter: Counter, total: int) -> List[CountItem]:
    items = [
        CountItem(label=label, count=count, percentage=round((count / total) * 100, 2) if total else 0.0)
        for label, count in counter.most_common()
    ]
    return items


def hospital_breakdown(df: pd.DataFrame) -> List[CountItem]:
    """Visit counts and percentages per hospital."""
    if df.empty:
        return []
    counter = Counter(df["hospital"].dropna().tolist())
    return _counter_to_items(counter, sum(counter.values()))


def doctor_breakdown(df: pd.DataFrame) -> List[CountItem]:
    if df.empty:
        return []
    counter = Counter(df["doctor"].dropna().tolist())
    return _counter_to_items(counter, sum(counter.values()))


def city_breakdown(df: pd.DataFrame) -> List[CountItem]:
    if df.empty:
        return []
    counter = Counter(df["city"].dropna().tolist())
    return _counter_to_items(counter, sum(counter.values()))


def disease_breakdown(df: pd.DataFrame, recurring_threshold: int = 2) -> Dict[str, object]:
    """Flatten disease arrays across all visits and compute frequency stats."""
    if df.empty:
        return {"frequencies": [], "top_diseases": [], "recurring_diseases": []}

    flattened: List[str] = []
    for diseases in df["diseases"].dropna():
        if isinstance(diseases, list):
            flattened.extend([d for d in diseases if d])
        elif isinstance(diseases, str) and diseases:
            flattened.append(diseases)

    counter = Counter(flattened)
    frequencies = _counter_to_items(counter, sum(counter.values()))
    top_diseases = [item.label for item in frequencies[:5]]
    recurring = [item.label for item in frequencies if item.count >= recurring_threshold]

    return {
        "frequencies": [f.model_dump() for f in frequencies],
        "top_diseases": top_diseases,
        "recurring_diseases": recurring,
    }


def visits_per_period(df: pd.DataFrame, freq: str = "M") -> List[Dict[str, object]]:
    """Visit counts bucketed by year (`freq='Y'`) or month (`freq='M'`)."""
    if df.empty:
        return []
    dates = pd.to_datetime(df["visit_date"], errors="coerce").dropna()
    if dates.empty:
        return []
    periods = dates.dt.to_period(freq)
    counts = periods.value_counts().sort_index()
    return [{"period": str(period), "count": int(count)} for period, count in counts.items()]


def claims_per_period(df: pd.DataFrame, freq: str = "Y") -> List[Dict[str, object]]:
    """Total claim amount bucketed by year or month."""
    if df.empty:
        return []
    work = df.copy()
    work["visit_date"] = pd.to_datetime(work["visit_date"], errors="coerce")
    work["claim_amount"] = pd.to_numeric(work["claim_amount"], errors="coerce")
    work = work.dropna(subset=["visit_date"])
    if work.empty:
        return []
    periods = work["visit_date"].dt.to_period(freq)
    grouped = work.groupby(periods)["claim_amount"].sum(min_count=1).sort_index()
    return [
        {"period": str(period), "total_claim": round(float(value), 2) if pd.notna(value) else 0.0}
        for period, value in grouped.items()
    ]


def claims_per_hospital(df: pd.DataFrame) -> List[Dict[str, object]]:
    if df.empty:
        return []
    work = df.copy()
    work["claim_amount"] = pd.to_numeric(work["claim_amount"], errors="coerce")
    grouped = work.groupby("hospital")["claim_amount"].sum(min_count=1).dropna().sort_values(ascending=False)
    return [{"hospital": hospital, "total_claim": round(float(v), 2)} for hospital, v in grouped.items()]


def disease_timeline(df: pd.DataFrame) -> List[Dict[str, object]]:
    """Chronological list of (date, diseases) pairs for timeline charting."""
    if df.empty:
        return []
    work = df.copy()
    work["visit_date"] = pd.to_datetime(work["visit_date"], errors="coerce")
    work = work.dropna(subset=["visit_date"]).sort_values("visit_date")
    return [
        {"date": row["visit_date"].date().isoformat(), "diseases": row["diseases"] or []}
        for _, row in work.iterrows()
    ]


def timeline_cards(df: pd.DataFrame, order: str = "desc") -> List[Dict[str, object]]:
    """Full visit timeline cards, sorted newest-first or oldest-first."""
    if df.empty:
        return []
    work = df.copy()
    work["_sort_date"] = pd.to_datetime(work["visit_date"], errors="coerce")
    work = work.sort_values("_sort_date", ascending=(order == "asc"), na_position="last")
    cards = []
    for _, row in work.iterrows():
        cards.append(
            {
                "record_id": row.get("record_id"),
                "visit_date": row["visit_date"].isoformat() if isinstance(row["visit_date"], pd.Timestamp) and pd.notna(row["visit_date"]) else row.get("visit_date"),
                "hospital": row.get("hospital"),
                "doctor": row.get("doctor"),
                "city": row.get("city"),
                "diseases": row.get("diseases") or [],
                "claim_amount": row.get("claim_amount"),
                "notes": row.get("notes"),
            }
        )
    return cards
