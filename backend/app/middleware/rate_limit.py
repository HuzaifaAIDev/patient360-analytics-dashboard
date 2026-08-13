"""
IP-based rate limiting middleware.

There is no login system in this app, so rate limiting is necessarily
IP-based rather than per-user. This is a small, dependency-free, in-memory
fixed-window limiter — no Redis, no extra third-party package — which is
appropriate for a single-process internal admin dashboard. It intentionally
keeps three separate buckets (general / search / export) since export and
search are the two operations worth limiting more tightly than everything
else.

Known limitation (documented rather than hidden): this in-memory approach
resets on restart and does not share state across multiple worker
processes/instances. A multi-worker or multi-instance production deployment
that needs strict, globally-consistent limits should replace the in-memory
store with a shared one (e.g. Redis) — the limiter's interface is small and
isolated to this one file specifically so that swap is easy later.
"""
from __future__ import annotations

import threading
import time
from typing import Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings
from app.utils.audit_log import audit_log

# Health checks must never be rate-limited, or monitoring breaks.
_EXEMPT_PATHS = {"/api/health"}


class _FixedWindowLimiter:
    """Per-key (IP, bucket) fixed-window request counter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Dict[Tuple[str, str, int], int] = {}

    def check(self, key: str, bucket: str, limit_per_minute: int) -> Tuple[bool, int]:
        """Returns (allowed, seconds_until_reset)."""
        window = int(time.time() // 60)
        counter_key = (key, bucket, window)

        with self._lock:
            # Opportunistically drop old windows so this dict doesn't grow
            # forever across a long-running process.
            stale = [k for k in self._counters if k[2] < window]
            for k in stale:
                del self._counters[k]

            count = self._counters.get(counter_key, 0) + 1
            self._counters[counter_key] = count

        seconds_until_reset = 60 - int(time.time() % 60)
        return count <= limit_per_minute, seconds_until_reset


_limiter = _FixedWindowLimiter()


def _bucket_for_path(path: str) -> str:
    if path.startswith("/api/export"):
        return "export"
    if path.startswith("/api/search"):
        return "search"
    return "general"


def _client_ip(request: Request) -> str:
    # Trust X-Forwarded-For only in the sense of reading it for identification
    # (not for any security decision beyond rate-limit bucketing) — a reverse
    # proxy (nginx/Cloudflare/etc.) is expected to set this correctly; a
    # direct, unproxied deployment falls back to the raw socket address.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()

        if not settings.rate_limit_enabled or request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        bucket = _bucket_for_path(request.url.path)
        limit = {
            "search": settings.rate_limit_search_per_minute,
            "export": settings.rate_limit_export_per_minute,
            "general": settings.rate_limit_general_per_minute,
        }[bucket]

        ip = _client_ip(request)
        allowed, retry_after = _limiter.check(ip, bucket, limit)

        if not allowed:
            audit_log("rate_limit_exceeded", ip=ip, bucket=bucket, path=request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down and try again shortly."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
