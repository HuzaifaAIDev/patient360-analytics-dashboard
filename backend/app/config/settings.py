"""
Application configuration.

All configurable values are loaded from environment variables (via a `.env`
file). Nothing is hardcoded — if a new configurable value is required, add it
here and to `.env.example`.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings sourced from environment variables."""

    # --- Application ---
    app_name: str = "Patient 360 Analytics Dashboard"
    app_env: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    default_timezone: str = "Asia/Karachi"

    # --- API documentation ---
    # Recommended: true in development, false in production (disables
    # /api/docs, /api/redoc, /api/openapi.json entirely).
    api_docs_enabled: bool = True

    # --- CORS ---
    # NOTE: there is deliberately no CORS_ORIGINS env var. Allowed origins are
    # controlled from the database (see the `allowed_origins` table / the
    # AllowedOrigin model) so they can be changed without redeploying the
    # app. This setting only controls how often the in-memory cache re-reads
    # that table.
    cors_cache_ttl_seconds: int = 30

    # --- Security headers ---
    # HSTS is only ever sent when BOTH of these are true AND the incoming
    # request actually arrived over HTTPS — never sent blindly over plain
    # HTTP local development, regardless of this flag.
    hsts_enabled: bool = True
    hsts_max_age_seconds: int = 31536000

    # --- Rate limiting (IP-based; there is no login, so no per-user limits) ---
    rate_limit_enabled: bool = True
    rate_limit_general_per_minute: int = 120
    rate_limit_search_per_minute: int = 60
    rate_limit_export_per_minute: int = 10

    # --- Request size limits ---
    # This app never accepts file uploads, so a small ceiling is plenty.
    max_request_body_bytes: int = 1_048_576  # 1 MB

    # --- AI ---
    ai_provider: str = "gemini"
    ai_api_key: str = ""
    ai_model: str = "gemini-1.5-flash"
    ai_timeout_seconds: int = 20
    ai_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    # --- Analytics ---
    recurring_disease_threshold: int = 2

    # --- Security (reserved) ---
    secret_key: str = "change-this-in-production"

    # --- Database ---
    # DATABASE_URL is the single source of truth for the connection and takes
    # priority if set. It supports any SQLAlchemy-compatible database:
    #   PostgreSQL : postgresql+psycopg2://user:password@host:5432/dbname
    #   MySQL      : mysql+pymysql://user:password@host:3306/dbname
    #   SQL Server : mssql+pyodbc://user:password@host:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server
    #   SQLite     : sqlite:///./patient360_dummy.db
    # If DATABASE_URL is left empty, it is built automatically from the
    # individual DB_* fields below — useful when a secrets manager injects
    # host/user/password separately rather than as one connection string.
    database_url: str = ""
    db_driver: str = "postgresql+psycopg2"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "patient360_db"
    db_user: str = "patient360_user"
    db_password: str = ""
    db_ssl_mode: str = "prefer"  # disable | allow | prefer | require | verify-ca | verify-full (Postgres)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout_seconds: int = 30
    db_pool_recycle_seconds: int = 1800
    db_echo_sql: bool = False
    db_connect_timeout_seconds: int = 10

    # --- SQL Server (mssql+pyodbc) specific ---
    # Requires the `pyodbc` package (in requirements.txt) AND the unixODBC
    # driver manager plus a Microsoft ODBC Driver installed at the OS level —
    # see docs/Database_Connection_Guide.pdf. Encryption defaults to ON with
    # certificate validation ON; do not weaken these for a real deployment.
    mssql_odbc_driver: str = "ODBC Driver 18 for SQL Server"
    mssql_encrypt: bool = True
    mssql_trust_server_certificate: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def ai_enabled(self) -> bool:
        return bool(self.ai_api_key and self.ai_api_key.strip())

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Resolve the final SQLAlchemy connection URL.

        Prefers the explicit `DATABASE_URL` env var. If that's not set, the
        URL is composed from the individual DB_* credential fields instead —
        this is what makes it possible to swap databases (SQLite for local
        dev, PostgreSQL/MySQL/SQL Server in production) purely through
        `.env`, with no code changes.
        """
        if self.database_url.strip():
            return self.database_url.strip()

        if self.db_driver.startswith("sqlite"):
            # SQLite has no user/password/host — just a file path as the "name"
            return f"sqlite:///{self.db_name}"

        password_segment = f":{self.db_password}" if self.db_password else ""
        base_url = f"{self.db_driver}://{self.db_user}{password_segment}@{self.db_host}:{self.db_port}/{self.db_name}"

        if self.db_driver.startswith("postgresql"):
            base_url += f"?sslmode={self.db_ssl_mode}&connect_timeout={self.db_connect_timeout_seconds}"
        elif self.db_driver.startswith("mssql"):
            driver_param = self.mssql_odbc_driver.replace(" ", "+")
            encrypt = "yes" if self.mssql_encrypt else "no"
            trust_cert = "yes" if self.mssql_trust_server_certificate else "no"
            base_url += (
                f"?driver={driver_param}&Encrypt={encrypt}&TrustServerCertificate={trust_cert}"
            )

        return base_url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"

    @property
    def resolved_driver_name(self) -> str:
        """
        The actual dialect+driver in effect, derived from the resolved
        connection URL rather than the DB_DRIVER field (which is only
        consulted when DATABASE_URL is empty) — used for accurate logging.
        """
        return self.sqlalchemy_database_url.split("://", 1)[0]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
