"""Unit tests for the database-backed CORS origin resolution."""
from __future__ import annotations

import time

import pytest

from app.db.session import Base, SessionLocal, engine
from app.db.models import AllowedOrigin
from app.services.cors_service import CorsOriginCache, DEFAULT_ORIGINS, ensure_default_origins


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    with SessionLocal() as db:
        db.query(AllowedOrigin).delete()
        db.commit()


def test_ensure_default_origins_populates_empty_table():
    ensure_default_origins()
    with SessionLocal() as db:
        rows = db.query(AllowedOrigin).all()
    assert len(rows) == len(DEFAULT_ORIGINS)
    origins = {r.origin for r in rows}
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
    assert all(r.is_active for r in rows)


def test_ensure_default_origins_is_a_noop_if_table_not_empty():
    with SessionLocal() as db:
        db.add(AllowedOrigin(origin="https://custom.example.com", is_active=True))
        db.commit()

    ensure_default_origins()

    with SessionLocal() as db:
        rows = db.query(AllowedOrigin).all()
    # Only the one custom row — defaults were NOT inserted alongside it.
    assert len(rows) == 1
    assert rows[0].origin == "https://custom.example.com"


def test_cache_only_returns_active_origins():
    with SessionLocal() as db:
        db.add(AllowedOrigin(origin="https://active.example.com", is_active=True))
        db.add(AllowedOrigin(origin="https://disabled.example.com", is_active=False))
        db.commit()

    cache = CorsOriginCache()
    origins = cache.get_origins()

    assert "https://active.example.com" in origins
    assert "https://disabled.example.com" not in origins


def test_cache_reflects_database_changes_after_invalidate():
    cache = CorsOriginCache()
    assert cache.get_origins() == []

    with SessionLocal() as db:
        db.add(AllowedOrigin(origin="https://new-origin.example.com", is_active=True))
        db.commit()

    # Without invalidating, a very fresh cache might still serve the old
    # (empty) result until its TTL expires — force a refresh to simulate
    # the TTL window passing.
    cache.invalidate()
    origins = cache.get_origins()
    assert "https://new-origin.example.com" in origins


def test_cache_survives_missing_table_gracefully(monkeypatch):
    """A refresh failure (e.g. DB hiccup) must not raise — it should keep serving the last-known list."""
    cache = CorsOriginCache()

    def _boom():
        raise RuntimeError("simulated database outage")

    monkeypatch.setattr(cache, "_refresh", _boom)
    # Should not raise, and should return whatever was cached before (empty on a fresh cache).
    origins = cache.get_origins()
    assert origins == []
