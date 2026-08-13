"""Export service: CSV, Excel, JSON, and PDF (patient report) generation."""
from __future__ import annotations

import io
from typing import Dict, List, Optional
from xml.sax.saxutils import escape as xml_escape

import orjson
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.patient import PatientSummaryStats

# Usable content width on an A4 page with 2cm left/right margins is exactly
# 17cm. Every table below is sized to a hair under that (16.8cm) so rounding
# in ReportLab's own cell padding can never push a table past the page edge.
_PAGE_CONTENT_WIDTH_CM = 16.8

_CELL_STYLE = ParagraphStyle(
    "TableCell",
    fontName="Helvetica",
    fontSize=8,
    leading=10.5,
    textColor=colors.HexColor("#1F2937"),
    wordWrap="CJK",  # wraps long unbroken strings (e.g. joined hospital lists) as well as normal text
)
_HEADER_CELL_STYLE = ParagraphStyle(
    "TableHeaderCell",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10.5,
    textColor=colors.white,
)


def _cell(value: object, style: ParagraphStyle = _CELL_STYLE) -> Paragraph:
    """
    Wrap arbitrary cell content in a Paragraph so ReportLab actually wraps
    long text (patient names, joined hospital/disease lists, etc.) within
    its column instead of overflowing past the column boundary — which is
    what previously produced misaligned, partially-hidden table columns.
    """
    text = "" if value is None else str(value)
    return Paragraph(xml_escape(text), style)


class ExportService:
    """Serializes patient/dataset records into various downloadable formats."""

    @staticmethod
    def to_csv_bytes(df: pd.DataFrame) -> bytes:
        buffer = io.StringIO()
        export_df = df.copy()
        if "diseases" in export_df.columns:
            export_df["diseases"] = export_df["diseases"].apply(
                lambda d: ", ".join(d) if isinstance(d, list) else d
            )
        export_df.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")

    @staticmethod
    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        export_df = df.copy()
        if "diseases" in export_df.columns:
            export_df["diseases"] = export_df["diseases"].apply(
                lambda d: ", ".join(d) if isinstance(d, list) else d
            )
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Records")
        return buffer.getvalue()

    @staticmethod
    def to_json_bytes(df: pd.DataFrame) -> bytes:
        records = df.to_dict(orient="records")
        return orjson.dumps(records, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS, default=str)

    @staticmethod
    def build_patient_pdf(
        stats: PatientSummaryStats,
        hospital_items: List[Dict],
        disease_items: List[Dict],
        timeline: List[Dict],
        ai_summary: Optional[str],
    ) -> bytes:
        """
        Build a professional multi-section PDF report for a single patient
        and return it as bytes, built entirely in memory (no temp file is
        ever written to disk, so there's nothing to clean up and no risk of
        generated reports accumulating over time).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=6)
        heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
        body_style = styles["BodyText"]

        story = []
        story.append(Paragraph("Patient 360 Analytics Report", title_style))
        story.append(Paragraph(f"Patient: {xml_escape(stats.patient_name)}", styles["Heading3"]))
        story.append(Spacer(1, 8))

        # --- Profile table ---
        story.append(Paragraph("Patient Profile", heading_style))
        profile_rows = [
            ["Total Records", str(stats.total_records)],
            ["Total Visits", str(stats.total_visits)],
            ["First Visit", str(stats.first_visit or "N/A")],
            ["Last Visit", str(stats.last_visit or "N/A")],
            ["Hospitals Visited", ", ".join(stats.hospitals_visited) or "N/A"],
            ["Doctors Consulted", ", ".join(stats.doctors_consulted) or "N/A"],
            ["Cities Visited", ", ".join(stats.cities_visited) or "N/A"],
            ["Average Claim", str(stats.average_claim if stats.average_claim is not None else "N/A")],
            ["Highest Claim", str(stats.highest_claim if stats.highest_claim is not None else "N/A")],
            ["Lowest Claim", str(stats.lowest_claim if stats.lowest_claim is not None else "N/A")],
            ["Total Claimed Amount", str(stats.total_claimed_amount if stats.total_claimed_amount is not None else "N/A")],
        ]
        story.append(_make_table(["Metric", "Value"], profile_rows, col_widths=[5.0, 11.8]))

        # --- Disease analysis ---
        story.append(Paragraph("Disease Analysis", heading_style))
        if disease_items:
            rows = [[d["label"], str(d["count"]), f"{d['percentage']}%"] for d in disease_items[:15]]
            story.append(_make_table(["Disease", "Count", "Percentage"], rows, col_widths=[9.8, 3.5, 3.5]))
        else:
            story.append(Paragraph("No disease data available.", body_style))

        # --- Hospital analysis ---
        story.append(Paragraph("Hospital Analysis", heading_style))
        if hospital_items:
            rows = [[h["label"], str(h["count"]), f"{h['percentage']}%"] for h in hospital_items[:15]]
            story.append(_make_table(["Hospital", "Visits", "Percentage"], rows, col_widths=[9.8, 3.5, 3.5]))
        else:
            story.append(Paragraph("No hospital data available.", body_style))

        # --- AI Summary ---
        story.append(Paragraph("AI Summary", heading_style))
        story.append(
            Paragraph(
                xml_escape(ai_summary or "AI summary is disabled because no API key is configured."),
                body_style,
            )
        )

        story.append(PageBreak())

        # --- Timeline ---
        story.append(Paragraph("Visit Timeline", heading_style))
        if timeline:
            rows = []
            for visit in timeline[:60]:
                diseases = ", ".join(visit.get("diseases") or [])
                rows.append(
                    [
                        str(visit.get("visit_date") or "N/A"),
                        str(visit.get("hospital") or "N/A"),
                        str(visit.get("doctor") or "N/A"),
                        diseases or "N/A",
                        str(visit.get("claim_amount") if visit.get("claim_amount") is not None else "N/A"),
                    ]
                )
            story.append(
                _make_table(
                    ["Date", "Hospital", "Doctor", "Diseases", "Claim"],
                    rows,
                    col_widths=[2.1, 3.2, 3.0, 6.0, 2.5],
                )
            )
        else:
            story.append(Paragraph("No visit history available.", body_style))

        doc.build(story)
        return buffer.getvalue()


def _make_table(header: List[str], rows: List[List[str]], col_widths: List[float]) -> Table:
    """
    Build a Table whose every cell is a wrapping Paragraph, sized to
    explicit column widths that always sum to within the printable page
    width. This is what prevents long values (hospital lists, disease
    arrays, long names) from overflowing their column and misaligning the
    rest of the row — every column now wraps onto additional lines instead.
    """
    widths = [w * cm for w in col_widths]
    header_row = [_cell(h, _HEADER_CELL_STYLE) for h in header]
    body_rows = [[_cell(value) for value in row] for row in rows]
    data = [header_row] + body_rows

    table = Table(data, colWidths=widths, repeatRows=1, splitByRow=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338CA")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


export_service = ExportService()
