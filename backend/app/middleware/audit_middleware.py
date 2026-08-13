"""
General request audit middleware.

Complements the targeted `audit_log(...)` calls made inside specific routes
(patient viewed, export generated, etc.) with a coarser net: any response
with a 4xx/5xx status is logged with method/path/status/IP, so unexpected or
security-related requests (malformed input, 404 probing, validation
failures, blocked CORS-adjacent requests, etc.) leave a trail even for
routes that don't have their own explicit audit_log call.

Never logs request/response bodies — only the metadata needed to answer
"who hit what, and what happened."
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.middleware.rate_limit import _client_ip
from app.utils.audit_log import audit_log


class RequestAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if response.status_code >= 400:
            audit_log(
                "request_error",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                ip=_client_ip(request),
            )

        return response
