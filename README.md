# Patient 360 Analytics Dashboard

**AI-powered Patient History Analytics Platform**

Search for any patient by name (with fuzzy matching) and instantly see their full medical history: every visit, hospital, doctor, recurring disease, claim statistics, an interactive analytics dashboard, and an optional AI-generated summary.

Every record is served from a **SQL database** — SQLite, PostgreSQL, MySQL, or SQL Server, your choice, configured entirely through environment variables. There is no JSON upload step in this application.

> **Demo Data Notice:** `patient360_dummy.db` contains synthetic data created exclusively for development, testing, demonstration, and educational purposes. It does not contain real patient information or confidential production company data. See [`SECURITY.md`](./SECURITY.md) for the full security policy.

> This is **not** a hospital management, registration, or appointment system. There is no login, no signup, no user accounts. The application opens directly into the dashboard. (The database connection itself *is* credentialed and access-controlled — see the security guide below — that's a separate concern from the app having no user-facing login screen.)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration (.env)](#configuration-env)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Running with Docker](#running-with-docker)
- [Production Build](#production-build)
- [Folder Structure](#folder-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security](#security)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Features

- 🗄️ **SQL-backed** — PostgreSQL, MySQL, or SQLite, switchable through `.env` alone, no code changes.
- 🔍 **Fuzzy patient search** — partial names, misspellings, and nicknames all resolve to the right patient (RapidFuzz), with live suggestions as you type.
- 📊 **Per-patient dashboard** — total records/visits, first/last visit, hospitals, doctors, cities, and claim statistics (average/highest/lowest/total).
- 🏥 **Hospital, doctor, city, and disease analytics** — frequency tables and interactive Plotly charts (bar, pie, line).
- 🩺 **Disease analytics** — diagnoses flattened across every visit, counted, and flagged as "recurring" once they cross a configurable threshold.
- 🕒 **Chronological timeline** — every visit as a card, sortable newest/oldest first.
- 🧾 **Full record table** — every field, sortable, filterable, paginated.
- 🤖 **AI Summary** — a Gemini-compatible LLM call generates a natural-language summary of the patient's history. **If no API key is configured, the app still works fully; the AI card just shows a friendly disabled message.**
- 📁 **Exports** — CSV, Excel, JSON, and a professional multi-page PDF report per patient, plus a print-optimized browser view.
- 🌗 **Dark / light mode**, glassmorphism cards, animated charts, loading skeletons, fully responsive.
- 🔐 **Credentialed, access-controlled database connection** — pooled, SSL-capable, parameterized queries throughout (see [Security](#security)).

---

## Architecture

```
┌─────────────────┐        REST/JSON        ┌──────────────────────┐        ┌───────────────────┐
│   React + TS      │ ───────────────────────▶│   FastAPI (Python)    │───────▶│   SQL Database      │
│   Vite frontend    │◀─────────────────────── │   Pandas analytics     │◀───────│ SQLite/PostgreSQL/  │
└─────────────────┘                          │   SQLAlchemy queries    │        │ MySQL (your choice)  │
                                              └──────────────────────┘        └───────────────────┘
                                                        │
                                              ┌──────────────────────┐
                                              │  Gemini-compatible AI │
                                              │  (optional, via .env) │
                                              └──────────────────────┘
```

`app/services/data_service.py` is the only place that queries the database; it loads the `patient_visits` table into a pandas DataFrame, and every analytics/search function downstream works against that DataFrame exactly as before — the storage layer is swappable without touching business logic.

**For the full picture — connection setup, how to point this at your own database, and the security model — see [`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf).**

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose
- (Optional) PostgreSQL or MySQL — not required for local dev; SQLite works out of the box

### Clone

```bash
git clone <your-fork-url> patient360
cd patient360
```

---

## Database Setup

The project ships with a **ready-to-use SQLite dummy database** (`backend/patient360_dummy.db`, 550 synthetic records across 80 patients) — zero setup required to try the app locally.

To point it at PostgreSQL, MySQL, or SQL Server instead, edit `backend/.env`:

```bash
# PostgreSQL
DATABASE_URL=postgresql+psycopg2://patient360_user:YOUR_PASSWORD@localhost:5432/patient360_db

# MySQL
DATABASE_URL=mysql+pymysql://patient360_user:YOUR_PASSWORD@localhost:3306/patient360_db

# SQL Server (requires unixODBC + a Microsoft ODBC Driver installed at the
# OS level — see docs/Database_Connection_Guide.pdf)
DATABASE_URL=mssql+pyodbc://patient360_user:YOUR_PASSWORD@localhost:1433/patient360_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no

# SQLite (default — no server needed)
DATABASE_URL=sqlite:///./patient360_dummy.db
```

Restart the backend after changing `.env` — it automatically creates the `patient_visits` table if it doesn't exist (safe/idempotent, never touches existing data).

To (re)seed a database with synthetic demo data:

```bash
cd backend
python -m scripts.seed_dummy_data              # 550 records (default)
python -m scripts.seed_dummy_data --reset --count 2000   # wipe and reseed with 2000 records
```

Full details — including least-privilege database users, SSL configuration, and troubleshooting — are in **[`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf)**.

---

## Configuration (.env)

All configuration lives in `backend/.env`. Copy the example and edit as needed:

```bash
cd backend
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Display name of the app | `Patient 360 Analytics Dashboard` |
| `APP_ENV` | `development` / `production` | `development` |
| `DEBUG` | Verbose error responses (dev only — never `true` in production) | `false` |
| `API_DOCS_ENABLED` | Serve `/api/docs`, `/api/redoc`, `/api/openapi.json` | `true` |
| `HOST` / `PORT` | Bind address for Uvicorn | `0.0.0.0` / `8000` |
| `LOG_LEVEL` | Python logging level | `INFO` |
| `CORS_CACHE_TTL_SECONDS` | How often the CORS origin cache re-reads the database | `30` |
| `HSTS_ENABLED` / `HSTS_MAX_AGE_SECONDS` | HSTS header (only ever sent over actual HTTPS) | `true` / `31536000` |
| `RATE_LIMIT_ENABLED` | Toggle IP-based rate limiting | `true` |
| `RATE_LIMIT_GENERAL_PER_MINUTE` / `RATE_LIMIT_SEARCH_PER_MINUTE` / `RATE_LIMIT_EXPORT_PER_MINUTE` | Per-bucket request limits | `120` / `60` / `10` |
| `MAX_REQUEST_BODY_BYTES` | Reject request bodies larger than this | `1048576` (1 MB) |
| `AI_PROVIDER` | AI provider identifier | `gemini` |
| `AI_API_KEY` | **Leave empty to disable AI summaries** | *(empty)* |
| `AI_MODEL` | Gemini model name | `gemini-1.5-flash` |
| `RECURRING_DISEASE_THRESHOLD` | Min. occurrences to flag "recurring" | `2` |
| `DATABASE_URL` | Full SQL connection string (takes priority if set) | `sqlite:///./patient360_dummy.db` |
| `DB_DRIVER` / `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Used only if `DATABASE_URL` is empty | see `.env.example` |
| `DB_SSL_MODE` | PostgreSQL SSL mode: disable/allow/prefer/require/verify-ca/verify-full | `prefer` |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` / `DB_POOL_TIMEOUT_SECONDS` / `DB_POOL_RECYCLE_SECONDS` | Connection pool tuning | see `.env.example` |
| `DB_ECHO_SQL` | Log every SQL statement (local debugging only — never enable in production) | `false` |
| `MSSQL_ODBC_DRIVER` / `MSSQL_ENCRYPT` / `MSSQL_TRUST_SERVER_CERTIFICATE` | SQL Server connection options (see below) | see `.env.example` |
| `SECRET_KEY` | Reserved for future use | *(placeholder)* |

**The application works completely without `AI_API_KEY`** — every feature except the AI Summary card remains fully functional.

---

## Running the Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env      # defaults to the bundled SQLite dummy database
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at `http://localhost:8000`, with interactive docs at `http://localhost:8000/api/docs`.

---

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite serves the app at `http://localhost:5173` and proxies `/api/*` requests to `http://localhost:8000`.

---

## Running with Docker

```bash
cp .env.example .env          # root .env — sets Postgres credentials for docker-compose
docker compose up --build
docker compose exec backend python -m scripts.seed_dummy_data   # load demo data
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432` (provisioned automatically as the `db` service)

---

## Production Build

**Backend**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend**:

```bash
cd frontend
npm run build      # outputs to frontend/dist
npm run preview    # serve the production build locally
```

Deploy `frontend/dist` behind any static file server or CDN, with `/api/*` reverse-proxied to the backend (see `frontend/nginx.conf`).

---

## Folder Structure

```
patient360/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── config/                # Settings loaded from .env
│   │   ├── db/                    # SQLAlchemy engine, session, ORM models
│   │   ├── routes/                # search, patient, analytics, export, database
│   │   ├── schemas/                # Pydantic models
│   │   ├── services/               # data_service (SQL), search_service, ai_service, export_service
│   │   ├── analytics/               # patient_analytics, global_analytics
│   │   └── utils/                  # logging_config
│   ├── scripts/
│   │   └── seed_dummy_data.py       # creates schema + inserts synthetic demo data
│   ├── tests/                       # pytest unit tests
│   ├── patient360_dummy.db          # ready-to-use SQLite dummy database
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                   # HomePage, PatientPage, DatabasePage, NotFoundPage
│   │   ├── components/              # SearchBar, Navbar, PlotlyChart, ui/, patient/
│   │   ├── hooks/                    # useTheme
│   │   ├── lib/                      # api.ts (Axios client)
│   │   └── types/                    # shared TS interfaces
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   └── Database_Connection_Guide.pdf  # connection setup + security deep-dive
├── docker-compose.yml                  # backend + frontend + PostgreSQL
├── .env.example                        # docker-compose Postgres credentials
├── Makefile
├── LICENSE
└── README.md
```

---

## API Documentation

Full interactive Swagger/OpenAPI docs are served by the backend at:

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### Key endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/search?q=` | Fuzzy patient name suggestions |
| `GET` | `/api/patient/{name}/stats` | Patient headline statistics |
| `GET` | `/api/patient/{name}/hospitals` \| `/doctors` \| `/cities` \| `/diseases` | Breakdown by dimension |
| `GET` | `/api/patient/{name}/timeline?order=asc\|desc` | Visit timeline cards |
| `GET` | `/api/patient/{name}/records` | Full record table |
| `GET` | `/api/patient/{name}/ai-summary` | AI summary (or disabled message) |
| `GET` | `/api/patient/{name}/charts/*` | Chart-ready aggregate series |
| `GET` | `/api/analytics/overview` | Dataset-wide KPIs and breakdowns |
| `GET` | `/api/export/{csv\|excel\|json\|pdf}?patient=` | Export data / PDF report |
| `GET` | `/api/database/status` | Live DB connectivity, driver, record counts |
| `GET` | `/api/database/cors-origins` | Currently allowed CORS origins (read-only) |
| `GET` | `/api/health` | Overall health check |

---

## Testing

```bash
cd backend
pytest -v
```

Database-layer tests run against an isolated, throwaway SQLite file — they never touch your real configured database. Covers the SQL-backed data service (record counts, DataFrame shape, diseases JSON round-tripping) and the analytics layer (stats, breakdowns, disease flattening, recurring-disease detection, claims aggregation).

---

## Security

See **[`SECURITY.md`](./SECURITY.md)** for the full security policy, and **[`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf)** for the database write-up. In short:

- Credentials live only in `backend/.env` (git-ignored) — never in source code.
- Every query goes through SQLAlchemy's parameterized query construction — no raw SQL string interpolation anywhere, which is what prevents SQL injection regardless of user input.
- Connection pooling is bounded (`DB_POOL_SIZE` / `DB_MAX_OVERFLOW`) so the app can never exhaust the database's connection limit.
- SSL/TLS is configurable per-database via `DB_SSL_MODE` (PostgreSQL) or `MSSQL_ENCRYPT` (SQL Server).
- **CORS-allowed origins are a database table (`allowed_origins`), not a `.env` value** — add, disable, or remove a row to change which frontends may call the API, without redeploying. A brand-new/empty database gets sensible localhost defaults automatically on first boot. There's a read-only `/api/database/cors-origins` endpoint (and a matching "Database" page in the app) to see what's currently allowed; there is deliberately no write endpoint for it, since an unauthenticated one would let anyone grant their own origin access — manage the table directly or via `scripts/seed_dummy_data.py`.
- **Security headers & CSP** on every response — `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and a `Content-Security-Policy` derived from this app's actual dependencies (Google Fonts, Plotly). Enforced both on the API (FastAPI middleware) and on the served frontend (`frontend/nginx.conf` in production). `Strict-Transport-Security` only sends when the request actually arrived over HTTPS.
- **IP-based rate limiting** (no login means no per-user limits): configurable general/search/export limits, health checks always exempt. Returns `429 Too Many Requests` with a `Retry-After` header.
- **Request size limits**, **filename sanitization** on every export (closes off header-injection/path-traversal via the `patient` query parameter), and **exports are generated entirely in memory** — no temp files ever written to disk.
- **Safe error handling**: production (`DEBUG=false`) never returns stack traces, SQL, or file paths — just a generic message, with full detail still logged server-side.
- `API_DOCS_ENABLED=false` disables `/api/docs`/`/api/redoc`/`/api/openapi.json` entirely for production deployments.
- The guide includes example SQL for creating a least-privilege database user, rather than connecting as a superuser.

---

## Future Enhancements

- Read replicas / connection routing for very large deployments
- Async SQLAlchemy (asyncpg) for higher-concurrency workloads
- Geo-mapped city analytics using real coordinates
- Configurable AI providers beyond Gemini-compatible endpoints
- Frontend component test suite (Vitest + Testing Library)

---

## License

MIT — see [LICENSE](./LICENSE).
