"""
Patient 360 Analytics Dashboard — FastAPI application entrypoint.

No authentication, no login, no user accounts on the application itself.
The application opens directly into the analytics dashboard. All patient
data lives in a SQL database (SQLite, PostgreSQL, MySQL, or SQL Server —
configured entirely through `.env`, see `app/config/settings.py`); the
database connection itself is protected by normal database
credentials/SSL, which is a separate concern from the app having no
user-facing login screen.

CORS is database-driven: allowed frontend origins are rows in the
`allowed_origins` table (see app/services/cors_service.py), not a static
.env value, so who's allowed to call this API can change without a
redeploy.

Middleware stack (outermost to innermost — see the add_middleware calls
below; Starlette applies the LAST-added middleware FIRST):
  1. RequestSizeLimitMiddleware — reject oversized requests before anything
     else does any work.
  2. SecurityHeadersMiddleware — wraps everything so every response,
     including ones short-circuited by rate limiting or CORS, still gets
     the standard security headers.
  3. RateLimitMiddleware — IP-based, since there is no login/user system.
  4. DatabaseBackedCORSMiddleware — allow-list resolved from the database.
  5. RequestAuditMiddleware — closest to the route handlers, logs the final
     response status for any 4xx/5xx.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.db.session import Base, check_database_connection, engine
from app.middleware.audit_middleware import RequestAuditMiddleware
from app.middleware.dynamic_cors import DatabaseBackedCORSMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_size_limit import RequestSizeLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routes import analytics, database, export, patient, search
from app.services.cors_service import cors_origin_cache, ensure_default_origins
from app.services.data_service import data_service
from app.utils.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("patient360.main")

app = FastAPI(
    title=settings.app_name,
    description="AI-powered Patient History Analytics Platform. No login required.",
    version="1.0.0",
    # Interactive API docs are disabled outright when API_DOCS_ENABLED=false
    # (recommended for production) rather than merely hidden — the schema
    # itself isn't served either.
    docs_url="/api/docs" if settings.api_docs_enabled else None,
    redoc_url="/api/redoc" if settings.api_docs_enabled else None,
    openapi_url="/api/openapi.json" if settings.api_docs_enabled else None,
)

# Registered in reverse of desired execution order — see module docstring.
app.add_middleware(RequestAuditMiddleware)
app.add_middleware(
    DatabaseBackedCORSMiddleware,
    get_allowed_origins=cors_origin_cache.get_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

app.include_router(search.router)
app.include_router(patient.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(database.router)


# ----------------------------------------------------------------------------
# Safe error handling: production responses never expose stack traces, SQL,
# file paths, or connection details. Development (DEBUG=true) keeps FastAPI's
# normal detailed behavior, which is far more useful while building the app.
# Validation errors (422) are left untouched in both modes — those are
# legitimate, safe, user-actionable feedback ("this field is required"), not
# an internal-details leak.
# ----------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def safe_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # HTTPException.detail is always something a route author deliberately
    # chose to surface (e.g. "No records found for patient 'X'.") — safe to
    # return as-is in both environments.
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    if settings.debug:
        # Local/dev convenience only — never reachable when DEBUG=false.
        return JSONResponse(status_code=500, content={"detail": f"{type(exc).__name__}: {exc}"})
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})


@app.on_event("startup")
async def verify_database() -> None:
    """
    Verify the configured SQL database is reachable, create the schema if it
    doesn't exist yet (safe/idempotent — only creates missing tables, never
    touches existing data), and make sure the `allowed_origins` table has at
    least sensible local-dev defaults so a brand new database doesn't lock
    the bundled frontend out of its own API. Never crashes the app: if the
    database is unreachable at boot, the app still starts and every
    data-dependent route (including CORS, which fails closed) will simply
    reflect that rather than 500-ing blindly.
    """
    connected, message = check_database_connection()
    if not connected:
        logger.error(
            "Could not connect to the configured database (%s): %s. "
            "Check DATABASE_URL / DB_* values in your .env file.",
            settings.sqlalchemy_database_url.split("@")[-1],  # never log credentials
            message,
        )
        return

    try:
        Base.metadata.create_all(bind=engine)
        ensure_default_origins()
    except Exception as exc:  # noqa: BLE001 - startup must never crash the app
        logger.warning("Database connected, but schema creation/check failed: %s", exc)
        return

    cors_origin_cache.invalidate()  # force a fresh read now that defaults may have been inserted

    logger.info(
        "Connected to database (%s driver). %s record(s) across %s patient(s). "
        "%s allowed CORS origin(s) configured. debug=%s api_docs_enabled=%s",
        settings.resolved_driver_name,
        data_service.record_count(),
        data_service.unique_patient_count(),
        len(cors_origin_cache.get_origins()),
        settings.debug,
        settings.api_docs_enabled,
    )


@app.get("/api/health", tags=["System"])
async def health_check():
    """
    Minimal liveness/health check — intentionally returns almost nothing.
    No credentials, connection strings, internal IPs, environment variables,
    file paths, or even record counts are exposed here; that's what
    /api/database/status is for (a separate, deliberately more detailed
    endpoint used by the in-app "Database" page). This endpoint's only job
    is answering "is the process up and can it reach its database" for
    uptime monitors, and it is intentionally exempt from rate limiting so
    monitoring never breaks.
    """
    connected, _ = check_database_connection()
    return {"status": "ok" if connected else "degraded"}
