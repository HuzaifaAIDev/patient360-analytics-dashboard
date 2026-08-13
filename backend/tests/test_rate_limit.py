"""Unit tests for the rate-limiting fixed-window counter."""
from __future__ import annotations

from app.middleware.rate_limit import _FixedWindowLimiter, _bucket_for_path


def test_allows_requests_under_the_limit():
    limiter = _FixedWindowLimiter()
    for _ in range(5):
        allowed, _ = limiter.check("1.2.3.4", "general", limit_per_minute=10)
        assert allowed is True


def test_blocks_requests_over_the_limit():
    limiter = _FixedWindowLimiter()
    for _ in range(5):
        limiter.check("1.2.3.4", "general", limit_per_minute=5)
    allowed, retry_after = limiter.check("1.2.3.4", "general", limit_per_minute=5)
    assert allowed is False
    assert retry_after > 0


def test_different_ips_have_independent_limits():
    limiter = _FixedWindowLimiter()
    for _ in range(5):
        limiter.check("1.1.1.1", "general", limit_per_minute=5)
    # A different IP should still be allowed even though 1.1.1.1 is exhausted.
    allowed, _ = limiter.check("2.2.2.2", "general", limit_per_minute=5)
    assert allowed is True


def test_different_buckets_have_independent_limits():
    limiter = _FixedWindowLimiter()
    for _ in range(5):
        limiter.check("1.2.3.4", "export", limit_per_minute=5)
    # The same IP hitting a different bucket (e.g. general browsing) should
    # not be blocked just because it exhausted the export bucket.
    allowed, _ = limiter.check("1.2.3.4", "search", limit_per_minute=5)
    assert allowed is True


def test_bucket_routing():
    assert _bucket_for_path("/api/export/pdf") == "export"
    assert _bucket_for_path("/api/search") == "search"
    assert _bucket_for_path("/api/patient/Ali/stats") == "general"
    assert _bucket_for_path("/api/analytics/overview") == "general"
