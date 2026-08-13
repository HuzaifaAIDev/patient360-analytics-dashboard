"""
Database engine and session management.

The engine is built once from `Settings.sqlalchemy_database_url`, which is
resolved entirely from environment variables (see `app/config/settings.py`
and `.env.example`) — no connection details are ever hardcoded here. This is
the single place in the codebase that knows how to talk to whichever
database the deployment is configured for (SQLite, PostgreSQL, MySQL, or
SQL Server).
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger("patient360.db")


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def _build_engine() -> Engine:
    settings = get_settings()
    url = settings.sqlalchemy_database_url

    connect_args = {}
    engine_kwargs: dict = {"echo": settings.db_echo_sql, "future": True}

    if settings.is_sqlite:
        # SQLite has no concept of a connection pool or network timeout, and
        # needs check_same_thread=False to be safely shared across FastAPI's
        # threadpool-backed request handlers.
        connect_args["check_same_thread"] = False
    else:
        # Real client/server databases (PostgreSQL, MySQL): use a bounded
        # connection pool so the app never opens unbounded connections
        # against the database, and recycle connections periodically so
        # stale/dropped connections don't linger.
        engine_kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout_seconds,
            pool_recycle=settings.db_pool_recycle_seconds,
            pool_pre_ping=True,  # detects and discards dead connections before use
        )
        if settings.db_driver.startswith("postgresql"):
            connect_args["connect_timeout"] = settings.db_connect_timeout_seconds
        elif settings.db_driver.startswith("mysql"):
            connect_args["connect_timeout"] = settings.db_connect_timeout_seconds
        elif settings.db_driver.startswith("mssql"):
            # pyodbc uses `timeout` (seconds) rather than `connect_timeout`.
            connect_args["timeout"] = settings.db_connect_timeout_seconds

    return create_engine(url, connect_args=connect_args, **engine_kwargs)


engine: Engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:  # noqa: ANN001
    """Enable foreign-key enforcement on SQLite connections (off by default)."""
    settings = get_settings()
    if settings.is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a request-scoped DB session, always closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for scripts/services that need a session outside of FastAPI's DI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str]:
    """
    Verify the configured database is reachable and credentials are valid.
    Used at startup and by the `/api/database/status` health endpoint.
    Never raises — always returns (ok, message) so the app can degrade
    gracefully and report a clear error instead of crashing.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Database connection successful."
    except Exception as exc:  # noqa: BLE001 - must never crash the app
        logger.error("Database connection failed: %s", exc)
        return False, str(exc)
