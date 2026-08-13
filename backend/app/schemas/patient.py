"""Pydantic schemas describing patient visit records and API payloads."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PatientVisit(BaseModel):
    """A single patient visit record, as stored in the `patient_visits` SQL table."""

    patient_name: str = Field(..., min_length=1, description="Full name of the patient")
    visit_date: Optional[date] = Field(None, description="Date of the visit (ISO format)")
    hospital: Optional[str] = Field(None, description="Hospital or clinic name")
    doctor: Optional[str] = Field(None, description="Attending doctor")
    city: Optional[str] = Field(None, description="City where the visit took place")
    diseases: List[str] = Field(default_factory=list, description="Diseases/diagnoses for this visit")
    claim_amount: Optional[float] = Field(None, ge=0, description="Insurance claim amount for this visit")
    notes: Optional[str] = Field(None, description="Free-text notes, if present")
    source_file: Optional[str] = Field(None, description="Originating data-load batch/source label")
    record_id: Optional[str] = Field(None, description="Deterministic ID assigned on ingestion")

    @field_validator("diseases", mode="before")
    @classmethod
    def coerce_diseases(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value

    @field_validator("patient_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class PatientSuggestion(BaseModel):
    """A single fuzzy-search suggestion."""

    patient_name: str
    score: float
    visit_count: int


class PatientSummaryStats(BaseModel):
    patient_name: str
    total_records: int
    total_visits: int
    first_visit: Optional[date]
    last_visit: Optional[date]
    hospitals_visited: List[str]
    doctors_consulted: List[str]
    cities_visited: List[str]
    average_claim: Optional[float]
    highest_claim: Optional[float]
    lowest_claim: Optional[float]
    total_claimed_amount: Optional[float]


class CountItem(BaseModel):
    label: str
    count: int
    percentage: float


class AISummaryResponse(BaseModel):
    enabled: bool
    summary: Optional[str] = None
    message: Optional[str] = None
