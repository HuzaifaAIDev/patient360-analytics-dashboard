"""Export endpoints: CSV, Excel, JSON, and PDF report generation."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.analytics import patient_analytics as pa
from app.config import get_settings
from app.services.ai_service import AIService
from app.services.data_service import data_service
from app.services.export_service import export_service
from app.services.search_service import search_service
from app.utils.audit_log import audit_log
from app.utils.sanitize import safe_filename

router = APIRouter(prefix="/api/export", tags=["Export"])

# Any single export size is capped defensively — this is a demo/internal
# analytics tool, not a bulk data-export platform. Prevents one request from
# forcing the server to serialize an unbounded number of rows.
_MAX_EXPORT_ROWS = 50_000


def _resolve_patient_df(name: str):
    df = data_service.dataframe
    if df.empty:
        return df, name
    if (df["patient_name"] == name).any():
        return df[df["patient_name"] == name], name
    resolved = search_service.best_match(df, name)
    if resolved is None:
        return df.iloc[0:0], name
    return df[df["patient_name"] == resolved], resolved


def _content_disposition(filename: str) -> dict:
    """Build a Content-Disposition header from an already-sanitized filename."""
    return {"Content-Disposition": f'attachment; filename="{filename}"'}


@router.get("/csv")
async def export_csv(patient: Optional[str] = Query(None, max_length=255)):
    df = data_service.dataframe if not patient else _resolve_patient_df(patient)[0]
    if df.empty:
        raise HTTPException(status_code=404, detail="No records available to export.")
    df = df.head(_MAX_EXPORT_ROWS)
    content = export_service.to_csv_bytes(df)
    filename = f"{safe_filename(patient, fallback='dataset')}_records.csv"
    audit_log("export_generated", export_format="csv", patient=bool(patient), rows=len(df))
    return Response(content=content, media_type="text/csv", headers=_content_disposition(filename))


@router.get("/excel")
async def export_excel(patient: Optional[str] = Query(None, max_length=255)):
    df = data_service.dataframe if not patient else _resolve_patient_df(patient)[0]
    if df.empty:
        raise HTTPException(status_code=404, detail="No records available to export.")
    df = df.head(_MAX_EXPORT_ROWS)
    content = export_service.to_excel_bytes(df)
    filename = f"{safe_filename(patient, fallback='dataset')}_records.xlsx"
    audit_log("export_generated", export_format="excel", patient=bool(patient), rows=len(df))
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=_content_disposition(filename),
    )


@router.get("/json")
async def export_json(patient: Optional[str] = Query(None, max_length=255)):
    df = data_service.dataframe if not patient else _resolve_patient_df(patient)[0]
    if df.empty:
        raise HTTPException(status_code=404, detail="No records available to export.")
    df = df.head(_MAX_EXPORT_ROWS)
    content = export_service.to_json_bytes(df)
    filename = f"{safe_filename(patient, fallback='dataset')}_records.json"
    audit_log("export_generated", export_format="json", patient=bool(patient), rows=len(df))
    return Response(content=content, media_type="application/json", headers=_content_disposition(filename))


@router.get("/pdf")
async def export_pdf(patient: str = Query(..., min_length=1, max_length=255)):
    """Generate a full PDF report for a single patient (profile, charts data, timeline, AI summary)."""
    settings = get_settings()
    patient_df, resolved_name = _resolve_patient_df(patient)
    if patient_df.empty:
        raise HTTPException(status_code=404, detail=f"No records found for patient '{patient}'.")

    stats = pa.compute_patient_stats(resolved_name, patient_df)
    diseases = pa.disease_breakdown(patient_df, settings.recurring_disease_threshold)
    hospitals = [i.model_dump() for i in pa.hospital_breakdown(patient_df)]
    timeline = pa.timeline_cards(patient_df, order="desc")

    ai_summary_text = None
    ai_service = AIService(settings)
    if ai_service.is_enabled():
        doctors = pa.doctor_breakdown(patient_df)
        result = await ai_service.generate_patient_summary(
            stats=stats,
            top_diseases=diseases["top_diseases"],
            recurring_diseases=diseases["recurring_diseases"],
            top_doctor=doctors[0].label if doctors else None,
            top_hospital=hospitals[0]["label"] if hospitals else None,
        )
        ai_summary_text = result.summary or result.message

    pdf_bytes = export_service.build_patient_pdf(
        stats=stats,
        hospital_items=hospitals,
        disease_items=diseases["frequencies"],
        timeline=timeline,
        ai_summary=ai_summary_text,
    )

    filename = f"{safe_filename(resolved_name, fallback='patient')}_report.pdf"
    audit_log("export_generated", export_format="pdf", patient=True, patient_name=resolved_name)
    return Response(content=pdf_bytes, media_type="application/pdf", headers=_content_disposition(filename))
