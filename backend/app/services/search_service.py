"""Fuzzy patient-name search, backed by RapidFuzz."""
from __future__ import annotations

from typing import List

import pandas as pd
from rapidfuzz import fuzz, process

from app.schemas.patient import PatientSuggestion


class SearchService:
    """Provides fuzzy/partial patient-name search over the unified dataset."""

    def suggest(self, df: pd.DataFrame, query: str, limit: int = 10) -> List[PatientSuggestion]:
        """Return up to `limit` fuzzy-matched patient name suggestions."""
        if df.empty or not query or not query.strip():
            return []

        visit_counts = df.groupby("patient_name").size().to_dict()
        unique_names = list(visit_counts.keys())

        matches = process.extract(
            query.strip(),
            unique_names,
            scorer=fuzz.WRatio,
            limit=limit,
        )

        suggestions = [
            PatientSuggestion(
                patient_name=name,
                score=round(float(score), 2),
                visit_count=int(visit_counts.get(name, 0)),
            )
            for name, score, _ in matches
            if score >= 45  # filter out very weak matches
        ]
        suggestions.sort(key=lambda s: (-s.score, -s.visit_count))
        return suggestions

    def best_match(self, df: pd.DataFrame, query: str) -> str | None:
        """Return the single best-matching patient name, or None."""
        suggestions = self.suggest(df, query, limit=1)
        return suggestions[0].patient_name if suggestions else None


search_service = SearchService()
