"""
Pytest configuration, shared across the whole test suite.

Runs before any test module is imported/collected, so it's the one place
that can safely redirect the app at a throwaway test database *before*
`app.db.session` builds its engine at import time. This guarantees tests
never touch the real database configured in `.env`, regardless of which
order pytest discovers test files in.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_patient360.db"
