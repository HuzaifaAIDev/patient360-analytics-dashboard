<p align="center">
  <img src="./docs/screenshots/banner.png" alt="Patient 360 Analytics Dashboard Banner" width="100%">
</p>

<h1 align="center">Patient 360 Analytics Dashboard</h1>

<p align="center">
  <strong>AI-Powered Patient History Analytics Platform</strong>
</p>

<p align="center">
  A full-stack healthcare analytics platform for searching, exploring, analyzing, visualizing, and exporting patient medical history from SQL databases.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLAlchemy-Database-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Pandas-Analytics-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly">
</p>

<p align="center">
  <a href="https://github.com/HuzaifaAIDev/patient360-analytics-dashboard">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL%20%7C%20MySQL%20%7C%20SQL%20Server-blue?style=flat-square" alt="Database Support">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License">
</p>

---

# 📌 Project Overview

**Patient 360 Analytics Dashboard** is a full-stack healthcare analytics and patient-history exploration platform.

The application allows users to search for patients using **fuzzy name matching** and instantly explore their complete medical history through a modern interactive dashboard.

Instead of manually searching through large healthcare datasets, users can access:

- Patient visit history
- Hospitals visited
- Doctors consulted
- Cities
- Diseases and diagnoses
- Recurring diseases
- Claim statistics
- Interactive analytics
- Chronological medical timelines
- Complete source records
- CSV exports
- Excel exports
- JSON exports
- Professional PDF reports

All patient records are retrieved directly from a **SQL database**.

> **Important:** This application does not use a JSON upload workflow. Patient data is read directly from the configured SQL database.

---

# ⚠️ Important Scope Notice

Patient 360 is specifically a **patient-history analytics and visualization platform**.

It is **not** a:

- Hospital management system
- Patient registration system
- Appointment management system
- Electronic medical record production system
- Billing management system
- Hospital administration system

The application does not include:

- Login
- Signup
- User accounts
- User registration
- Appointment scheduling

The application opens directly into the analytics dashboard.

> Database authentication and application user authentication are separate concerns. The application can connect to a credentialed and access-controlled database even though it does not provide a user-facing login screen.

---

# 🧪 Demo Data Notice

The repository contains a bundled SQLite database:

```text
backend/patient360_dummy.db
```

This database contains **synthetic/demo data** created exclusively for:

- Development
- Testing
- Demonstration
- Educational purposes
- Portfolio presentation

It does **not** contain:

- Real patient information
- Protected health information
- Confidential production company information

### Current Demo Dataset

| Metric | Value |
|---|---:|
| Synthetic Records | **550** |
| Unique Patients | **80** |
| Hospitals | **7** |
| Database | **SQLite** |
| Search | **Fuzzy Matching** |
| Analytics | **Plotly** |
| Backend | **FastAPI + Python** |
| Frontend | **React + TypeScript** |
| AI | **Optional** |

See [`SECURITY.md`](./SECURITY.md) for the complete security policy.

---

# 📸 Screenshots

## 🏠 Main Dashboard

The main dashboard provides a high-level overview of the complete dataset, including patient counts, records, hospitals, claims, diseases, visits, and doctor frequency.

![Patient 360 Dashboard](./docs/screenshots/dashboard.png)

---

## 📊 Patient Analytics

Interactive patient-level analytics provide insights into disease frequency, disease distribution, hospital visits, doctor frequency, and other patient dimensions.

![Patient Analytics](./docs/screenshots/patient_analytics.png)

---

## 👤 Patient Overview

The patient overview provides key statistics and a summarized view of an individual patient's medical history.

![Patient Overview](./docs/screenshots/patient_overview.png)

---

## 🕒 Patient Timeline

The chronological timeline displays every recorded visit, including visit date, hospital, doctor, diseases, claim amount, and visit notes.

![Patient Timeline](./docs/screenshots/patient_timeline.png)

---

## 📋 Patient Records & Export

The complete records table provides filtering, sorting, pagination, and export functionality.

Supported export formats include:

- CSV
- Excel
- JSON
- PDF

![Patient Records](./docs/screenshots/patient_records.png)

---

## 🗄️ Database Connection

The database page displays live database information including database connectivity, driver information, record counts, patient counts, and allowed frontend origins.

![Database Connection](./docs/screenshots/database.png)

---

# ✨ Key Features

## 🔍 Fuzzy Patient Search

Patients can be searched using approximate names.

The search system supports:

- Full names
- Partial names
- Misspellings
- Similar spellings
- Approximate input
- Nickname-like input

The application uses **RapidFuzz** for fuzzy matching.

Example:

```text
Search:
Muhammad Huzaifa

Possible matching results:
Muhammad Huzaifa
Muhammad H. Huzaifa
Muhamad Huzaifa
Muhammad Huzaifah
```

This makes the system more practical when dealing with imperfect or inconsistent patient names.

---

# 📊 Patient Analytics

Each patient receives a dedicated analytics view containing:

- Total records
- Total visits
- First visit
- Last visit
- Average claim
- Highest claim
- Lowest claim
- Total claimed amount
- Hospitals visited
- Doctors consulted
- Cities visited
- Diseases diagnosed

---

# 🏥 Healthcare Analytics

The platform provides analytics across multiple healthcare dimensions:

- Hospitals
- Doctors
- Cities
- Diseases
- Visits
- Claims

Interactive visualizations are created using **Plotly**.

---

# 🩺 Disease Analytics

Disease information is analyzed across patient visits.

The system provides:

- Disease frequency
- Disease distribution
- Disease share
- Patient-specific disease analytics
- Recurring disease detection

The recurring disease threshold can be configured through the environment file.

Example:

```env
RECURRING_DISEASE_THRESHOLD=2
```

With a threshold of `2`, a disease appearing at least twice can be classified as recurring.

---

# 🕒 Medical Visit Timeline

Each patient's history can be displayed chronologically.

The timeline includes:

- Visit date
- Hospital
- Doctor
- Diseases
- Claim amount
- Visit notes

Users can switch between:

```text
Newest First
Oldest First
```

This provides a simple way to understand how a patient's healthcare history developed over time.

---

# 📋 Complete Medical Records

The records interface provides access to the underlying patient records.

Features include:

- Complete records
- Sorting
- Filtering
- Pagination
- Disease information
- Claim information
- Hospital information
- Doctor information
- City information
- Visit notes
- Source information

---

# 📁 Export System

Patient information can be exported into multiple formats.

### Supported formats

```text
CSV
Excel
JSON
PDF
```

The PDF export generates a professional multi-page patient report.

The application also supports a print-optimized browser view.

---

# 🤖 Optional AI Patient Summary

Patient 360 contains an **optional Gemini-compatible AI integration**.

When an AI API key is configured, the application can generate a natural-language summary of a patient's medical history.

However, **AI is not required for the application to work**.

### Current Development Configuration

If no AI API key is available, simply leave:

```env
AI_API_KEY=
```

empty.

The application continues to provide all core functionality:

```text
Patient Search
      ↓
Patient Overview
      ↓
Analytics
      ↓
Timeline
      ↓
Records
      ↓
Exports
```

Only the optional AI summary functionality remains disabled.

> **Note:** The current demonstration environment does not have an AI API key configured. Therefore, the AI section is intentionally not showcased in the screenshots.

---

# 🌗 Modern User Interface

The frontend includes:

- Dark mode
- Light mode
- Responsive layout
- Modern dashboard
- Glassmorphism-style cards
- Interactive charts
- Loading skeletons
- Responsive tables
- Modern navigation
- Mobile-friendly layouts
- Interactive patient analytics

---

# 🔐 Security Features

Security has been considered throughout the application architecture.

The backend includes:

- Parameterized SQLAlchemy queries
- Database connection pooling
- SSL/TLS configuration
- CORS management
- Security headers
- Content Security Policy
- HSTS support
- IP-based rate limiting
- Request-size limits
- Filename sanitization
- Path traversal protection
- Safe production error handling
- Environment-based secrets
- API documentation toggle
- No database credentials stored in source code

See [`SECURITY.md`](./SECURITY.md) for the complete security policy.

For detailed database configuration and security guidance, see:

[`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf)

---

# 🛠️ Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Type-safe frontend development |
| Vite | Frontend development and build tool |
| Tailwind CSS | Styling |
| Plotly | Interactive analytics |
| Axios | API communication |

---

## Backend

| Technology | Purpose |
|---|---|
| Python | Backend and data processing |
| FastAPI | REST API |
| SQLAlchemy | Database abstraction and ORM |
| Pandas | Data analytics |
| RapidFuzz | Fuzzy patient search |
| Pydantic | Data validation |
| Uvicorn | ASGI server |
| ReportLab | PDF generation |
| OpenPyXL | Excel export |
| Pytest | Automated testing |

---

# 🗄️ Database Support

Patient 360 supports multiple SQL database engines:

```text
SQLite
PostgreSQL
MySQL
Microsoft SQL Server
```

The database can be changed through environment configuration without changing the application's business logic.

---

# 🏗️ System Architecture

```text
┌───────────────────────────────────────┐
│          React + TypeScript           │
│             Vite Frontend             │
└──────────────────┬────────────────────┘
                   │
                   │ REST / JSON
                   ▼
┌───────────────────────────────────────┐
│            FastAPI Backend            │
│               Python                  │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │           API Routes            │  │
│  └───────────────┬─────────────────┘  │
│                  │                    │
│  ┌───────────────▼─────────────────┐  │
│  │            Services             │  │
│  │                                 │  │
│  │ Data / Search / Analytics       │  │
│  │ Export / AI / CORS              │  │
│  └───────────────┬─────────────────┘  │
│                  │                    │
│  ┌───────────────▼─────────────────┐  │
│  │       SQLAlchemy + Pandas       │  │
│  └───────────────┬─────────────────┘  │
└──────────────────┼────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│             SQL Database              │
│                                       │
│ SQLite / PostgreSQL / MySQL / MSSQL  │
└───────────────────────────────────────┘
                   │
                   │ Optional
                   ▼
┌───────────────────────────────────────┐
│       Gemini-Compatible AI            │
│        Patient Summary                │
└───────────────────────────────────────┘
```

---

# 🔄 Data Flow

```text
SQL Database
     │
     ▼
SQLAlchemy
     │
     ▼
Data Service
     │
     ▼
Pandas DataFrame
     │
     ├─────────────────────┐
     │                     │
     ▼                     ▼
Search Service         Analytics
     │                     │
     │                     ├── Patient Analytics
     │                     ├── Disease Analytics
     │                     ├── Hospital Analytics
     │                     ├── Doctor Analytics
     │                     └── Claim Analytics
     │
     ▼
FastAPI REST API
     │
     ▼
React Frontend
     │
     ├── Dashboard
     ├── Patient Overview
     ├── Analytics
     ├── Timeline
     ├── Records
     └── Export
```

---

# 🗄️ Database Architecture

The database layer is designed to remain independent from the analytics and presentation layers.

Supported databases:

```text
SQLite
PostgreSQL
MySQL
Microsoft SQL Server
```

The primary patient data table is:

```text
patient_visits
```

Database access is centralized through:

```text
backend/app/services/data_service.py
```

The service layer retrieves SQL-backed records and provides them to the analytics and search layers.

This design makes it possible to change the underlying database without rewriting the application's business logic.

---

# 🚀 Installation

## Prerequisites

Install:

- Python 3.11+
- Node.js 20+
- npm
- Git

Optional:

- Docker
- Docker Compose
- PostgreSQL
- MySQL
- Microsoft SQL Server

SQLite is already included for local demonstration.

---

# 📥 Clone the Repository

```bash
git clone https://github.com/HuzaifaAIDev/patient360-analytics-dashboard.git
cd patient360-analytics-dashboard
```

---

# 🐍 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment.

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

If PowerShell blocks script execution, you can use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ⚙️ Configure Environment Variables

Copy the example environment file.

### Windows

```powershell
copy .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

The default configuration uses the bundled SQLite database.

---

# 🗃️ Bundled SQLite Database

The repository already includes:

```text
backend/patient360_dummy.db
```

Therefore, no database server is required for the first local run.

The bundled demo database contains:

```text
550 synthetic records
80 unique patients
```

---

# ▶️ Run the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/api/docs
```

ReDoc:

```text
http://localhost:8000/api/redoc
```

---

# ⚛️ Frontend Setup

Open a second terminal.

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Vite normally serves the frontend at:

```text
http://localhost:5173
```

The frontend communicates with the FastAPI backend through the configured API proxy.

---

# 🗄️ Database Configuration

The default database is SQLite.

```env
DATABASE_URL=sqlite:///./patient360_dummy.db
```

The application can also connect to other supported databases.

---

## PostgreSQL

Example:

```env
DATABASE_URL=postgresql+psycopg2://patient360_user:YOUR_PASSWORD@localhost:5432/patient360_db
```

---

## MySQL

Example:

```env
DATABASE_URL=mysql+pymysql://patient360_user:YOUR_PASSWORD@localhost:3306/patient360_db
```

---

## Microsoft SQL Server

Example:

```env
DATABASE_URL=mssql+pyodbc://patient360_user:YOUR_PASSWORD@localhost:1433/patient360_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no
```

SQL Server requires the appropriate Microsoft ODBC driver to be installed on the operating system.

For detailed SQL Server setup and troubleshooting:

[`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf)

---

# 🌱 Seed Synthetic Data

The project includes a synthetic data seeding script.

From the backend directory:

```bash
python -m scripts.seed_dummy_data
```

Default:

```text
550 synthetic records
```

To reset and generate a different number of records:

```bash
python -m scripts.seed_dummy_data --reset --count 2000
```

> Use the `--reset` option only with a development or demo database.

---

# ⚙️ Environment Configuration

Backend configuration is controlled through:

```text
backend/.env
```

The template is:

```text
backend/.env.example
```

Important configuration options include:

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | Patient 360 Analytics Dashboard |
| `APP_ENV` | Application environment | development |
| `DEBUG` | Development debug mode | false |
| `API_DOCS_ENABLED` | Enable Swagger/ReDoc | true |
| `HOST` | Uvicorn host | 0.0.0.0 |
| `PORT` | Backend port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |
| `DATABASE_URL` | SQLAlchemy connection URL | SQLite |
| `DB_DRIVER` | Database driver | See `.env.example` |
| `DB_HOST` | Database host | See `.env.example` |
| `DB_PORT` | Database port | See `.env.example` |
| `DB_NAME` | Database name | See `.env.example` |
| `DB_USER` | Database username | See `.env.example` |
| `DB_PASSWORD` | Database password | See `.env.example` |
| `DB_SSL_MODE` | PostgreSQL SSL mode | prefer |
| `DB_POOL_SIZE` | Database connection pool size | See `.env.example` |
| `DB_MAX_OVERFLOW` | Maximum pool overflow | See `.env.example` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_GENERAL_PER_MINUTE` | General request limit | 120 |
| `RATE_LIMIT_SEARCH_PER_MINUTE` | Search request limit | 60 |
| `RATE_LIMIT_EXPORT_PER_MINUTE` | Export request limit | 10 |
| `MAX_REQUEST_BODY_BYTES` | Maximum request body | 1048576 |
| `RECURRING_DISEASE_THRESHOLD` | Recurring disease threshold | 2 |
| `AI_PROVIDER` | AI provider | gemini |
| `AI_API_KEY` | Optional AI API key | Empty |
| `AI_MODEL` | AI model | See `.env.example` |
| `HSTS_ENABLED` | Enable HSTS | true |
| `DB_ECHO_SQL` | SQL debugging | false |

---

# 🤖 AI Configuration

The AI functionality is optional.

If you have an AI API key, it can be configured through:

```env
AI_API_KEY=YOUR_API_KEY
```

If you do **not** have an API key, leave it empty:

```env
AI_API_KEY=
```

The application will continue to work normally.

The following features do **not** require an AI API key:

```text
Fuzzy Search
Patient Overview
Patient Analytics
Disease Analytics
Hospital Analytics
Doctor Analytics
Timeline
Records
CSV Export
Excel Export
JSON Export
PDF Export
Database Monitoring
```

Only the optional AI patient summary is disabled.

---

# 🐳 Docker

The project includes Docker configuration for:

- Backend
- Frontend
- PostgreSQL

From the project root:

```bash
docker compose up --build
```

Typical endpoints:

```text
Frontend:  http://localhost:5173
Backend:   http://localhost:8000
PostgreSQL: localhost:5432
```

To seed the PostgreSQL database inside Docker:

```bash
docker compose exec backend python -m scripts.seed_dummy_data
```

---

# 🏭 Production Build

## Backend

Example production command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production, configure:

```env
APP_ENV=production
DEBUG=false
```

It is also recommended to disable API documentation in production when it is not required:

```env
API_DOCS_ENABLED=false
```

---

## Frontend

Build the production frontend:

```bash
cd frontend
npm run build
```

The production output will be generated in:

```text
frontend/dist
```

The project also includes:

```text
frontend/nginx.conf
```

for production frontend serving and API reverse-proxy configuration.

---

# 📡 API Documentation

When the backend is running, interactive OpenAPI documentation is available.

### Swagger UI

```text
http://localhost:8000/api/docs
```

### ReDoc

```text
http://localhost:8000/api/redoc
```

---

# 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/search?q=` | Fuzzy patient search |
| `GET` | `/api/patient/{name}/stats` | Patient statistics |
| `GET` | `/api/patient/{name}/hospitals` | Hospital breakdown |
| `GET` | `/api/patient/{name}/doctors` | Doctor breakdown |
| `GET` | `/api/patient/{name}/cities` | City breakdown |
| `GET` | `/api/patient/{name}/diseases` | Disease breakdown |
| `GET` | `/api/patient/{name}/timeline` | Patient timeline |
| `GET` | `/api/patient/{name}/records` | Complete patient records |
| `GET` | `/api/patient/{name}/ai-summary` | Optional AI summary |
| `GET` | `/api/patient/{name}/charts/*` | Patient chart data |
| `GET` | `/api/analytics/overview` | Dataset-wide analytics |
| `GET` | `/api/export/csv` | CSV export |
| `GET` | `/api/export/excel` | Excel export |
| `GET` | `/api/export/json` | JSON export |
| `GET` | `/api/export/pdf` | PDF report |
| `GET` | `/api/database/status` | Database connectivity |
| `GET` | `/api/database/cors-origins` | Allowed CORS origins |
| `GET` | `/api/health` | API health check |

---

# 🧪 Testing

Backend tests are located in:

```text
backend/tests/
```

Run the complete test suite:

```bash
cd backend
pytest -v
```

The test suite covers areas including:

- Analytics
- Configuration
- CORS service
- Data service
- Rate limiting
- Input sanitization
- Security middleware
- Database functionality

Database tests use isolated SQLite test databases so they do not modify the configured development or production database.

---

# 🔐 Security

Security is implemented at multiple layers of the application.

## Database Security

The application uses:

- SQLAlchemy parameterized queries
- No raw SQL interpolation
- Credential-based database connections
- Connection pooling
- SSL/TLS configuration
- Environment-based credentials
- Least-privilege database configuration guidance

---

## API Security

The backend includes:

- Security headers
- Content Security Policy
- HSTS support
- Rate limiting
- Request body size limits
- Safe error handling
- CORS controls
- Filename sanitization
- Path traversal protection

---

## Security Headers

Supported security headers include:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
Permissions-Policy
Content-Security-Policy
Strict-Transport-Security
```

---

## Rate Limiting

The API provides configurable IP-based rate limiting.

Separate limits can be configured for:

```text
General Requests
Search Requests
Export Requests
```

When a configured limit is exceeded, the API can return:

```text
429 Too Many Requests
```

with an appropriate retry response.

---

## Environment Secrets

Sensitive credentials should only be stored in:

```text
backend/.env
```

The `.env` file should never be committed to Git.

The repository provides:

```text
backend/.env.example
```

as a safe configuration template.

---

# 📂 Project Structure

```text
patient360-analytics-dashboard/
│
├── backend/
│   ├── app/
│   │   ├── analytics/
│   │   │   ├── global_analytics.py
│   │   │   └── patient_analytics.py
│   │   │
│   │   ├── config/
│   │   │   └── settings.py
│   │   │
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── audit_middleware.py
│   │   │   ├── dynamic_cors.py
│   │   │   ├── rate_limit.py
│   │   │   ├── request_size_limit.py
│   │   │   └── security_headers.py
│   │   │
│   │   ├── routes/
│   │   │   ├── analytics.py
│   │   │   ├── database.py
│   │   │   ├── export.py
│   │   │   ├── patient.py
│   │   │   └── search.py
│   │   │
│   │   ├── schemas/
│   │   │   └── patient.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── cors_service.py
│   │   │   ├── data_service.py
│   │   │   ├── export_service.py
│   │   │   └── search_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── audit_log.py
│   │   │   ├── logging_config.py
│   │   │   └── sanitize.py
│   │   │
│   │   └── main.py
│   │
│   ├── scripts/
│   │   └── seed_dummy_data.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_analytics.py
│   │   ├── test_config.py
│   │   ├── test_cors_service.py
│   │   ├── test_data_service.py
│   │   ├── test_rate_limit.py
│   │   ├── test_sanitize.py
│   │   └── test_security_middleware.py
│   │
│   ├── patient360_dummy.db
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── patient/
│   │   │   └── ui/
│   │   │
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docs/
│   ├── Database_Connection_Guide.pdf
│   └── screenshots/
│       ├── banner.png
│       ├── dashboard.png
│       ├── patient-analytics.png
│       ├── patient-overview.png
│       ├── patient-timeline.png
│       ├── patient-records.png
│       └── database.png
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
├── Makefile
├── SECURITY.md
└── README.md
```

---

# 🧠 Design Decisions

## Database Abstraction

The application does not hard-code business logic around SQLite.

Database configuration is controlled through environment variables.

This allows the same application architecture to work with:

```text
SQLite
PostgreSQL
MySQL
Microsoft SQL Server
```

---

## Data Service Separation

Database access is centralized in:

```text
backend/app/services/data_service.py
```

This separates database operations from analytics, API routing, and presentation logic.

---

## Analytics Separation

Analytics functionality is organized inside:

```text
backend/app/analytics/
```

including:

```text
patient_analytics.py
global_analytics.py
```

This keeps analytical calculations independent from the API routing layer.

---

## Service-Based Backend

Business functionality is separated into dedicated services:

```text
data_service
search_service
export_service
ai_service
cors_service
```

This improves:

- Maintainability
- Testability
- Code organization
- Scalability
- Future extensibility

---

# 📚 Documentation

Additional documentation is available in the repository.

## Database Connection Guide

[`docs/Database_Connection_Guide.pdf`](./docs/Database_Connection_Guide.pdf)

The guide covers:

- SQLite configuration
- PostgreSQL configuration
- MySQL configuration
- SQL Server configuration
- Connection security
- SSL configuration
- Database credentials
- Least-privilege users
- Troubleshooting

---

## Security Policy

[`SECURITY.md`](./SECURITY.md)

The security documentation covers:

- Security architecture
- Database security
- API security
- CORS
- Rate limiting
- Security headers
- Secret management
- Error handling

---

# 📊 Current Demo Dataset

| Metric | Value |
|---|---:|
| Synthetic Patient Records | **550** |
| Unique Patients | **80** |
| Hospitals | **7** |
| Database | **SQLite** |
| Search | **Fuzzy Matching** |
| Analytics | **Plotly** |
| Backend | **FastAPI** |
| Frontend | **React + TypeScript** |
| AI | **Optional** |
| Export Formats | **CSV / Excel / JSON / PDF** |

---

# 💼 Portfolio Highlights

This project demonstrates practical experience with:

```text
Python
FastAPI
React
TypeScript
SQL
SQLAlchemy
Pandas
Data Analytics
Data Visualization
Plotly
REST APIs
Fuzzy Search
Database Abstraction
SQLite
PostgreSQL
MySQL
Microsoft SQL Server
Docker
Docker Compose
Nginx
API Security
Rate Limiting
CORS
Security Headers
Automated Testing
PDF Generation
Excel Export
Data Engineering
Optional AI Integration
```

The project combines:

```text
Full-Stack Development
        +
Data Analytics
        +
Data Visualization
        +
Database Engineering
        +
REST API Development
        +
Security
        +
Testing
        +
Reporting
```

into a single healthcare analytics platform.

---

# 🔮 Future Enhancements

Potential future improvements include:

- Frontend component testing with Vitest
- React Testing Library
- CI/CD pipeline
- Automated deployment
- Read replicas for large-scale databases
- Database connection routing
- Async SQLAlchemy
- Advanced geographic analytics
- Interactive geographic maps
- Configurable AI providers
- Additional export formats
- Advanced dashboard filtering
- Role-based access control
- Audit dashboard
- Production monitoring
- Application metrics
- Centralized logging
- Advanced caching
- Performance optimization for very large datasets

---

# 👨‍💻 Author

## Hafiz Muhammad Huzaifa

**AI & Data Science Developer**

### GitHub

[github.com/HuzaifaAIDev](https://github.com/HuzaifaAIDev)

### Project Repository

[Patient 360 Analytics Dashboard](https://github.com/HuzaifaAIDev/patient360-analytics-dashboard)

### Email

[muhammadhuzaifawd1st@gmail.com](mailto:muhammadhuzaifawd1st@gmail.com)

### Contact

**0326-3090980**

---

# 📄 License

This project is licensed under the **MIT License**.

See [`LICENSE`](./LICENSE) for details.

---

# ⭐ Support the Project

If you find this project useful for:

- Learning
- Data analytics
- Full-stack development
- Healthcare analytics
- Portfolio development
- Experimentation

consider giving the repository a ⭐ on GitHub.

---

# 📌 Project Summary

**Patient 360 Analytics Dashboard** transforms SQL-backed patient records into a modern, searchable, interactive analytics experience.

The platform combines:

```text
React + TypeScript
        ↓
FastAPI + Python
        ↓
SQLAlchemy
        ↓
Pandas
        ↓
SQLite / PostgreSQL / MySQL / SQL Server
        ↓
Analytics + Visualization + Reporting
```

with an optional:

```text
Gemini-Compatible AI
        ↓
Patient History Summary
```

The application demonstrates how structured healthcare data can be transformed into a professional analytics platform featuring:

- Modern React frontend
- FastAPI backend
- SQL database abstraction
- Fuzzy patient search
- Patient-level analytics
- Disease analytics
- Hospital and doctor analytics
- Interactive Plotly visualizations
- Medical timelines
- Complete patient records
- CSV/Excel/JSON/PDF exports
- Database flexibility
- API security
- Rate limiting
- CORS controls
- Security headers
- Automated testing
- Docker support
- Production deployment structure
- Optional AI integration

> **Patient 360 — Patient History Analytics, Simplified.**

---

<p align="center">
  <strong>Built by Hafiz Muhammad Huzaifa</strong>
</p>

<p align="center">
  <a href="https://github.com/HuzaifaAIDev/patient360-analytics-dashboard">
    ⭐ View Patient 360 on GitHub
  </a>
</p>
