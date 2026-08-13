"""
Integration tests for the security middleware stack, exercised through the
real FastAPI app (not just the isolated unit-level pieces tested elsewhere).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.session import Base, engine
from app.main import app
from app.middleware import rate_limit as rate_limit_module


@pytest.fixture(autouse=True)
def _fresh_schema_and_rate_limiter():
    """Fresh schema per test, and a clean rate-limit counter so tests don't bleed into each other."""
    Base.metadata.create_all(bind=engine)
    rate_limit_module._limiter = rate_limit_module._FixedWindowLimiter()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_security_headers_present(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_hsts_not_sent_over_plain_http(client):
    response = client.get("/api/health")
    assert "Strict-Transport-Security" not in response.headers


def test_health_check_returns_minimal_response(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"status"}


def test_health_check_is_exempt_from_rate_limiting(client):
    settings = get_settings()
    # Hammer health well past the general limit — it must never 429.
    for _ in range(settings.rate_limit_general_per_minute + 20):
        response = client.get("/api/health")
        assert response.status_code == 200


def test_general_rate_limit_triggers_429(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_general_per_minute", 3)

    statuses = [client.get("/api/analytics/dataset-status").status_code for _ in range(5)]
    assert 429 in statuses
    # And the 429 response carries a Retry-After header.
    blocked_index = statuses.index(429)
    assert blocked_index >= 3  # first 3 should have succeeded before blocking


def test_rate_limited_response_has_retry_after_header(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_general_per_minute", 1)

    client.get("/api/analytics/dataset-status")
    response = client.get("/api/analytics/dataset-status")
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_search_and_export_buckets_are_independent(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_search_per_minute", 2)
    monkeypatch.setattr(settings, "rate_limit_general_per_minute", 100)

    for _ in range(2):
        client.get("/api/search", params={"q": "ali"})
    blocked = client.get("/api/search", params={"q": "ali"})
    assert blocked.status_code == 429

    # A completely different bucket (general) should be unaffected.
    ok = client.get("/api/analytics/dataset-status")
    assert ok.status_code == 200


def test_oversized_request_body_rejected(client):
    settings = get_settings()
    big_body = b"x" * (settings.max_request_body_bytes + 1000)
    response = client.post("/api/health", content=big_body)
    assert response.status_code == 413


def test_404_returns_safe_error_shape(client):
    response = client.get("/api/patient/Definitely Not A Real Patient XYZ/stats")
    assert response.status_code == 404
    body = response.json()
    assert set(body.keys()) == {"detail"}
    assert "Definitely Not A Real Patient XYZ" in body["detail"]


def test_validation_error_returns_422_with_detail(client):
    # limit=0 violates ge=1 on /api/search
    response = client.get("/api/search", params={"q": "a", "limit": 0})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_search_query_max_length_enforced(client):
    response = client.get("/api/search", params={"q": "a" * 200})
    assert response.status_code == 422


def test_docs_available_when_enabled_by_default(client):
    # backend/.env.example ships with API_DOCS_ENABLED=true (development
    # default) — confirms the docs_url wiring in main.py actually works.
    response = client.get("/api/docs")
    assert response.status_code == 200
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
