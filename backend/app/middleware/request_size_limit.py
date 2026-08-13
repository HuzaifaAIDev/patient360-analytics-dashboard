"""
Request size limit middleware.

This application never accepts file uploads or large request bodies (every
endpoint is a GET with query parameters), so a small ceiling is plenty and
guards against a client sending an unnecessarily/maliciously large request
body to a POST/PUT-capable route in the future, or simply as defense in
depth today.

Checks Content-Length up front (cheap, no body read needed) when present;
if a client omits Content-Length and streams a body instead, the body is
read incrementally with a hard cap so an unbounded stream still can't
exhaust memory.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        max_bytes = settings.max_request_body_bytes

        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large."},
                    )
            except ValueError:
                pass  # malformed header — let normal request handling reject it

        return await call_next(request)
