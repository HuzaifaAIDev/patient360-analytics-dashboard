"""
Security headers middleware.

Adds standard defensive headers to every API response. Most of these are
meaningful even on a pure JSON API (e.g. X-Content-Type-Options stops a
browser from trying to sniff/execute a JSON response as something else),
and are included here as defense-in-depth / to satisfy automated security
header scanners hitting the API directly.

Note on Content-Security-Policy: this backend never serves the frontend's
HTML document (that's Vite in dev, nginx in production — see
frontend/nginx.conf and frontend/vite.config.ts for where CSP is actually
enforced for the page itself). CSP on a JSON API response has no browser
effect on how the SPA page behaves, but it's included here too, harmlessly,
for completeness/consistency across every response this service returns.

HSTS is only ever added when the request actually arrived over HTTPS AND
hsts_enabled is on — never sent blindly over local plain HTTP, which would
otherwise make local development impossible to use over http://localhost.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings

_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "font-src 'self' data:; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'; "
    "form-action 'self'"
)

# Note: below is a more permissive CSP than the one above, which is stricter and
# may break some browsers' handling of the Vite dev server. The stricter one
# is commented out above, and the more permissive one is used here. In production,
# the frontend's nginx config will enforce a stricter CSP for the SPA page itself,
# but this backend middleware is just for API responses, so a more permissive
# CSP is acceptable here.

# _CSP = (
#     "default-src 'self'; "
#     "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
#     "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
#     "img-src 'self' data: https://cdn.jsdelivr.net; "
#     "connect-src 'self'; "
#     "font-src 'self' data: https://cdn.jsdelivr.net; "
#     "object-src 'none'; "
#     "base-uri 'self'; "
#     "frame-ancestors 'none'; "
#     "form-action 'self'"
# )



class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        settings = get_settings()

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = _CSP

        is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        if settings.hsts_enabled and is_https:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age_seconds}; includeSubDomains"
            )

        return response
