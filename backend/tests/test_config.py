"""
Tests for configuration-driven security behavior.

These construct fresh `Settings()` instances directly rather than mutating
the shared `get_settings()` singleton, so they can't leak state into other
test modules that share the same lru_cache'd settings object.
"""
from __future__ import annotations

from app.config import get_settings
from app.config.settings import Settings


def test_debug_defaults_to_false():
    # Production safety: DEBUG must default to off, not on.
    settings = Settings(_env_file=None)
    assert settings.debug is False


def test_mssql_url_includes_driver_and_encryption_params():
    settings = Settings(
        _env_file=None,
        database_url="",
        db_driver="mssql+pyodbc",
        db_host="sql.example.com",
        db_port=1433,
        db_name="patient360_db",
        db_user="app_user",
        db_password="secret",
        mssql_odbc_driver="ODBC Driver 18 for SQL Server",
        mssql_encrypt=True,
        mssql_trust_server_certificate=False,
    )

    url = settings.sqlalchemy_database_url

    assert url.startswith("mssql+pyodbc://app_user:secret@sql.example.com:1433/patient360_db")
    assert "driver=ODBC+Driver+18+for+SQL+Server" in url
    assert "Encrypt=yes" in url
    assert "TrustServerCertificate=no" in url


def test_mssql_url_respects_trust_server_certificate_override():
    settings = Settings(_env_file=None, database_url="", db_driver="mssql+pyodbc", mssql_trust_server_certificate=True)
    url = settings.sqlalchemy_database_url
    assert "TrustServerCertificate=yes" in url


def test_database_url_takes_priority_over_individual_fields():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg2://explicit:url@host/db",
        db_driver="mssql+pyodbc",  # should be ignored
    )
    assert settings.sqlalchemy_database_url == "postgresql+psycopg2://explicit:url@host/db"


def test_sqlite_url_needs_no_credentials():
    settings = Settings(_env_file=None, database_url="", db_driver="sqlite", db_name="test_only.db")
    assert settings.sqlalchemy_database_url == "sqlite:///test_only.db"


def test_is_production_flag():
    assert Settings(_env_file=None, app_env="production").is_production is True
    assert Settings(_env_file=None, app_env="development").is_production is False


def test_resolved_driver_name_reflects_actual_url_not_fallback_field():
    settings = Settings(
        _env_file=None,
        database_url="sqlite:///./patient360_dummy.db",
        db_driver="postgresql+psycopg2",  # should be ignored for display purposes
    )
    assert settings.resolved_driver_name == "sqlite"


def test_app_settings_singleton_is_unaffected_by_these_tests():
    # Sanity check that the shared cached settings the rest of the app uses
    # (pinned to the isolated test DB by tests/conftest.py) were never
    # touched by the isolated Settings() instances constructed above.
    settings = get_settings()
    assert "test_patient360.db" in settings.database_url
