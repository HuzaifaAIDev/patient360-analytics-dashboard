"""Aggregate analytics computed across the entire (multi-patient) dataset."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd

from app.analytics.patient_analytics import (
    city_breakdown,
    disease_breakdown,
    doctor_breakdown,
    hospital_breakdown,
    visits_per_period,
)


def dataset_overview(df: pd.DataFrame, recurring_threshold: int = 2) -> Dict[str, object]:
    """High-level KPIs and breakdowns across every patient in the dataset."""
    if df.empty:
        return {
            "total_records": 0,
            "unique_patients": 0,
            "total_hospitals": 0,
            "total_doctors": 0,
            "total_cities": 0,
            "total_claimed_amount": 0.0,
            "hospital_breakdown": [],
            "doctor_breakdown": [],
            "city_breakdown": [],
            "disease_breakdown": {"frequencies": [], "top_diseases": [], "recurring_diseases": []},
            "visits_per_month": [],
            "visits_per_year": [],
        }

    claims = pd.to_numeric(df["claim_amount"], errors="coerce").dropna()

    return {
        "total_records": len(df),
        "unique_patients": int(df["patient_name"].nunique()),
        "total_hospitals": int(df["hospital"].dropna().nunique()),
        "total_doctors": int(df["doctor"].dropna().nunique()),
        "total_cities": int(df["city"].dropna().nunique()),
        "total_claimed_amount": round(float(claims.sum()), 2) if not claims.empty else 0.0,
        "hospital_breakdown": [i.model_dump() for i in hospital_breakdown(df)],
        "doctor_breakdown": [i.model_dump() for i in doctor_breakdown(df)],
        "city_breakdown": [i.model_dump() for i in city_breakdown(df)],
        "disease_breakdown": disease_breakdown(df, recurring_threshold),
        "visits_per_month": visits_per_period(df, freq="M"),
        "visits_per_year": visits_per_period(df, freq="Y"),
    }


def top_patients_by_visits(df: pd.DataFrame, limit: int = 10) -> List[Dict[str, object]]:
    if df.empty:
        return []
    counts = df.groupby("patient_name").size().sort_values(ascending=False).head(limit)
    return [{"patient_name": name, "visit_count": int(count)} for name, count in counts.items()]
