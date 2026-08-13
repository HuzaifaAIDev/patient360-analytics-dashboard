"""Dataset-wide (all-patient) analytics endpoints, powering the overview dashboard."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.analytics.global_analytics import dataset_overview, top_patients_by_visits
from app.config import get_settings
from app.services.data_service import data_service
from app.utils.audit_log import audit_log

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_overview():
    settings = get_settings()
    df = data_service.dataframe
    audit_log("analytics_requested", scope="overview", records=len(df))
    return dataset_overview(df, settings.recurring_disease_threshold)


@router.get("/top-patients")
async def get_top_patients(limit: int = Query(10, ge=1, le=100)):
    df = data_service.dataframe
    return top_patients_by_visits(df, limit=limit)


@router.get("/dataset-status")
async def dataset_status():
    return {
        "total_records": data_service.record_count(),
        "unique_patients": data_service.unique_patient_count(),
        "is_empty": data_service.is_empty(),
    }
