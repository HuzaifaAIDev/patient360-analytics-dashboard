"""Per-patient dashboard endpoints."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from app.analytics import patient_analytics as pa
from app.config import get_settings
from app.schemas.patient import AISummaryResponse, PatientSummaryStats
from app.services.ai_service import AIService
from app.services.data_service import data_service
from app.services.search_service import search_service
from app.utils.audit_log import audit_log

router = APIRouter(prefix="/api/patient", tags=["Patient"])

# A single patient's full record set is inherently bounded by real-world
# visit history, but this caps it defensively anyway so a pathological
# amount of data for one name can never make a single response unbounded.
_MAX_RECORDS_PER_PATIENT = 10_000

# Shared path-parameter constraint for every /patient/{name}/... route: a
# reasonable maximum length rejects malformed/abusive input before it ever
# reaches the fuzzy-matching or DataFrame-filtering logic.
_NamePath = Path(..., min_length=1, max_length=255, description="Patient name (exact or fuzzy)")


def _get_patient_df(name: str, exact: bool = True):
    df = data_service.dataframe
    if df.empty:
        return df, name
    if exact and (df["patient_name"] == name).any():
        return df[df["patient_name"] == name], name
    # fall back to fuzzy best-match resolution
    resolved = search_service.best_match(df, name)
    if resolved is None:
        return df.iloc[0:0], name
    return df[df["patient_name"] == resolved], resolved


@router.get("/{name}/stats", response_model=PatientSummaryStats)
async def get_patient_stats(name: str = _NamePath) -> PatientSummaryStats:
    patient_df, resolved_name = _get_patient_df(name, exact=False)
    if patient_df.empty:
        raise HTTPException(status_code=404, detail=f"No records found for patient '{name}'.")
    audit_log("patient_viewed", patient_name=resolved_name)
    return pa.compute_patient_stats(resolved_name, patient_df)


@router.get("/{name}/hospitals")
async def get_patient_hospitals(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return [i.model_dump() for i in pa.hospital_breakdown(patient_df)]


@router.get("/{name}/doctors")
async def get_patient_doctors(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return [i.model_dump() for i in pa.doctor_breakdown(patient_df)]


@router.get("/{name}/cities")
async def get_patient_cities(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return [i.model_dump() for i in pa.city_breakdown(patient_df)]


@router.get("/{name}/diseases")
async def get_patient_diseases(name: str = _NamePath):
    settings = get_settings()
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.disease_breakdown(patient_df, settings.recurring_disease_threshold)


@router.get("/{name}/timeline")
async def get_patient_timeline(name: str = _NamePath, order: Literal["asc", "desc"] = Query("desc")):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.timeline_cards(patient_df, order=order)


@router.get("/{name}/charts/visits-per-month")
async def get_visits_per_month(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.visits_per_period(patient_df, freq="M")


@router.get("/{name}/charts/visits-per-year")
async def get_visits_per_year(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.visits_per_period(patient_df, freq="Y")


@router.get("/{name}/charts/claims-per-year")
async def get_claims_per_year(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.claims_per_period(patient_df, freq="Y")


@router.get("/{name}/charts/claims-per-hospital")
async def get_claims_per_hospital(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.claims_per_hospital(patient_df)


@router.get("/{name}/charts/disease-timeline")
async def get_disease_timeline(name: str = _NamePath):
    patient_df, _ = _get_patient_df(name, exact=False)
    return pa.disease_timeline(patient_df)


@router.get("/{name}/records")
async def get_patient_records(name: str = _NamePath):
    """Full record table for this patient (every JSON field, for the data grid)."""
    patient_df, _ = _get_patient_df(name, exact=False)
    if patient_df.empty:
        return []
    return patient_df.head(_MAX_RECORDS_PER_PATIENT).to_dict(orient="records")


@router.get("/{name}/ai-summary", response_model=AISummaryResponse)
async def get_ai_summary(name: str = _NamePath) -> AISummaryResponse:
    settings = get_settings()
    patient_df, resolved_name = _get_patient_df(name, exact=False)
    if patient_df.empty:
        raise HTTPException(status_code=404, detail=f"No records found for patient '{name}'.")

    stats = pa.compute_patient_stats(resolved_name, patient_df)
    diseases = pa.disease_breakdown(patient_df, settings.recurring_disease_threshold)
    hospitals = pa.hospital_breakdown(patient_df)
    doctors = pa.doctor_breakdown(patient_df)

    ai_service = AIService(settings)
    return await ai_service.generate_patient_summary(
        stats=stats,
        top_diseases=diseases["top_diseases"],
        recurring_diseases=diseases["recurring_diseases"],
        top_doctor=doctors[0].label if doctors else None,
        top_hospital=hospitals[0].label if hospitals else None,
    )
