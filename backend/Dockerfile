FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# unixodbc: ODBC driver *manager* required to actually connect via
# mssql+pyodbc (SQL Server support). This does NOT include Microsoft's own
# ODBC Driver 17/18 for SQL Server, which requires accepting Microsoft's
# license and adding their apt repository — see
# docs/Database_Connection_Guide.pdf for those steps. Without it, SQLite/
# PostgreSQL/MySQL connections are unaffected; only mssql+pyodbc URLs need
# it at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Production safety: no --reload here (that's for local development only —
# see `make backend`, which does use --reload). Behind a reverse proxy
# (nginx/Cloudflare/etc.), scale with --workers as needed, e.g.:
#   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
#
# On container start: verify DB connectivity/create schema (handled by the
# app's startup event in app/main.py), then serve the API. To load the
# bundled dummy dataset (or reseed a fresh database), run:
#   docker compose exec backend python -m scripts.seed_dummy_data
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
