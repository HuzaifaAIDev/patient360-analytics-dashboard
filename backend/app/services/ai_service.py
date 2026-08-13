"""
AI summary generation service.

Uses a Gemini-compatible REST API when `AI_API_KEY` is configured. If no key
is configured, or the call fails/times out, the service degrades gracefully
and the rest of the application continues to function normally.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import Settings
from app.schemas.patient import AISummaryResponse, PatientSummaryStats

logger = logging.getLogger("patient360.ai_service")

DISABLED_MESSAGE = "AI summary is disabled because no API key is configured."
FAILURE_MESSAGE = "AI summary is temporarily unavailable. Please try again later."


class AIService:
    """Generates a natural-language patient summary via a Gemini-compatible API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_enabled(self) -> bool:
        return self._settings.ai_enabled

    async def generate_patient_summary(
        self,
        stats: PatientSummaryStats,
        top_diseases: list[str],
        recurring_diseases: list[str],
        top_doctor: Optional[str],
        top_hospital: Optional[str],
    ) -> AISummaryResponse:
        """Generate an AI summary for a patient, or return a disabled/failure message."""
        if not self.is_enabled():
            return AISummaryResponse(enabled=False, message=DISABLED_MESSAGE)

        prompt = self._build_prompt(stats, top_diseases, recurring_diseases, top_doctor, top_hospital)

        url = (
            f"{self._settings.ai_base_url}/models/{self._settings.ai_model}:generateContent"
            f"?key={self._settings.ai_api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 500},
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.ai_timeout_seconds) as client:
                response = await client.post(url, json=body)
                response.raise_for_status()
                data = response.json()
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
                )
                if not text:
                    raise ValueError("Empty response from AI provider")
                return AISummaryResponse(enabled=True, summary=text)
        except httpx.TimeoutException:
            logger.warning("AI summary request timed out")
            return AISummaryResponse(enabled=True, message=FAILURE_MESSAGE)
        except Exception as exc:  # noqa: BLE001 - deliberately broad, must never crash the app
            logger.warning("AI summary generation failed: %s", exc)
            return AISummaryResponse(enabled=True, message=FAILURE_MESSAGE)

    @staticmethod
    def _build_prompt(
        stats: PatientSummaryStats,
        top_diseases: list[str],
        recurring_diseases: list[str],
        top_doctor: Optional[str],
        top_hospital: Optional[str],
    ) -> str:
        return (
            "You are a clinical data analyst assistant. Write a concise, factual, "
            "3-5 sentence summary of the following patient's medical history for "
            "an internal analytics dashboard. Do not invent facts not present below. "
            "Mention recurring conditions, hospital/doctor usage patterns, and claim "
            "behavior. Avoid definitive diagnoses; describe patterns only.\n\n"
            f"Patient: {stats.patient_name}\n"
            f"Total visits: {stats.total_visits} (records: {stats.total_records})\n"
            f"First visit: {stats.first_visit}, Last visit: {stats.last_visit}\n"
            f"Hospitals visited: {', '.join(stats.hospitals_visited) or 'N/A'}\n"
            f"Doctors consulted: {', '.join(stats.doctors_consulted) or 'N/A'}\n"
            f"Cities visited: {', '.join(stats.cities_visited) or 'N/A'}\n"
            f"Most frequent hospital: {top_hospital or 'N/A'}\n"
            f"Most frequent doctor: {top_doctor or 'N/A'}\n"
            f"Top diseases: {', '.join(top_diseases) or 'N/A'}\n"
            f"Recurring diseases (threshold met): {', '.join(recurring_diseases) or 'None'}\n"
            f"Average claim: {stats.average_claim}, Total claimed: {stats.total_claimed_amount}, "
            f"Highest claim: {stats.highest_claim}, Lowest claim: {stats.lowest_claim}\n"
        )
