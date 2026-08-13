"""
Database-backed CORS origin resolution.

Allowed origins are rows in the `allowed_origins` table, not a static
`.env` value — this lets whoever administers the database add, disable, or
remove an allowed frontend origin without redeploying the backend. Because
checking the database on *every single request* would be wasteful, results
are cached in memory for `Settings.cors_cache_ttl_seconds` (default 30s) and
refreshed lazily.

If the database is briefly unreachable when a refresh is due, the previous
cached list keeps being served rather than the app rejecting every request
— a failed refresh degrades to "stick with what we last knew," not
"suddenly block all origins."
"""
from __future__ import annotations

import logging
import threading
import time
from typing import List

from sqlalchemy import select

from app.config import get_settings
from app.db.models import AllowedOrigin
from app.db.session import SessionLocal

logger = logging.getLogger("patient360.cors")

# Sensible out-of-the-box defaults so a freshly created database (e.g. right
# after `python -m scripts.seed_dummy_data`, or on first boot against an
# empty DB) doesn't lock out the bundled frontend dev server. Anyone
# administering the database is free to disable/remove these later.
DEFAULT_ORIGINS = [
    ("http://localhost:5173", "Vite dev server (default)"),
    ("http://127.0.0.1:5173", "Vite dev server (default, 127.0.0.1)"),
]


class CorsOriginCache:
    """Thread-safe, TTL-based in-memory cache over the `allowed_origins` table."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cached_origins: List[str] = []
        self._last_refreshed_at: float = 0.0

    def _ttl_seconds(self) -> int:
        return get_settings().cors_cache_ttl_seconds

    def _refresh(self) -> None:
        with SessionLocal() as db:
            rows = db.execute(
                select(AllowedOrigin.origin).where(AllowedOrigin.is_active.is_(True))
            ).scalars().all()
        with self._lock:
            self._cached_origins = list(rows)
            self._last_refreshed_at = time.time()

    def get_origins(self) -> List[str]:
        """Return the current allowed-origins list, refreshing the cache if stale."""
        stale = (time.time() - self._last_refreshed_at) > self._ttl_seconds()
        if stale:
            try:
                self._refresh()
            except Exception as exc:  # noqa: BLE001 - never let a DB hiccup break CORS entirely
                logger.warning("Could not refresh allowed origins from the database: %s", exc)
        with self._lock:
            return list(self._cached_origins)

    def invalidate(self) -> None:
        """Force the next lookup to hit the database instead of the cache."""
        with self._lock:
            self._last_refreshed_at = 0.0


cors_origin_cache = CorsOriginCache()


def ensure_default_origins() -> None:
    """
    Insert the default local-dev origins if the `allowed_origins` table is
    completely empty. Only ever runs once per fresh database — if a row
    already exists (even a disabled one), this is a no-op, since that means
    someone has already taken ownership of this table's contents.
    """
    with SessionLocal() as db:
        existing = db.execute(select(AllowedOrigin.id).limit(1)).first()
        if existing is not None:
            return
        for origin, note in DEFAULT_ORIGINS:
            db.add(AllowedOrigin(origin=origin, is_active=True, note=note))
        db.commit()
        logger.info("allowed_origins table was empty — inserted %s default origin(s).", len(DEFAULT_ORIGINS))
