"""Patient search endpoint."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Query

from app.schemas.patient import PatientSuggestion
from app.services.data_service import data_service
from app.services.search_service import search_service
from app.utils.audit_log import audit_log

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("", response_model=List[PatientSuggestion])
async def search_patients(
    q: str = Query(..., min_length=1, max_length=100, description="Partial or fuzzy patient name"),
    limit: int = Query(10, ge=1, le=50),
) -> List[PatientSuggestion]:
    """Return fuzzy-matched patient name suggestions for the search-as-you-type box."""
    df = data_service.dataframe
    results = search_service.suggest(df, q, limit=limit)
    audit_log("patient_searched", query_length=len(q), results=len(results))
    return results
