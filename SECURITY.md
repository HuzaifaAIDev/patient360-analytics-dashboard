# Security Policy

## Intended Use

Patient 360 Analytics Dashboard is built for **controlled, internal use** —
an analytics tool run inside an organization's own network, not a
public-facing consumer product. It does not currently implement login,
signup, user accounts, or role-based access control, by design (see
`README.md`). Access to a deployed instance should be restricted through
your own infrastructure: a private network, VPN, reverse proxy with IP
allow-listing, or similar — the application itself does not gate who can
reach it.

If your deployment needs per-user authentication or access control, put it
in front of this application (e.g. at a reverse proxy, VPN, or SSO gateway)
rather than expecting the application to provide it.

## Demo Data

`backend/patient360_dummy.db` contains **synthetic data only**, generated
programmatically for development, testing, demonstration, and educational
purposes. It does not contain real patient information, real hospital
records, or confidential production data of any kind. Do not replace it
with, or commit, real patient data to this repository.

## What This Repository Does and Does Not Claim

This project implements a range of technical security controls (see below).
It does **not** claim to be HIPAA-compliant, GDPR-compliant, SOC 2 compliant,
or ISO-certified. Compliance with any of those frameworks is an
organizational and legal process — covering things like policies, staff
training, data processing agreements, and formal audits — that goes well
beyond what any codebase can claim on its own. If you plan to process real
patient/health data with a deployment of this project, get that formally
assessed by qualified people before you do.

## Security Controls Implemented

- **Database credentials** live only in `backend/.env` (git-ignored, never
  committed); `.env.example` ships with placeholder values only.
- **SQL injection**: every query goes through SQLAlchemy's parameterized
  query construction — no raw string-interpolated SQL anywhere in the
  codebase.
- **CORS**: allowed origins are a database table (`allowed_origins`), not a
  static wildcard or hardcoded list; the middleware fails closed if the
  origin cache/database lookup itself errors.
- **Security headers**: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`, and a `Content-Security-Policy`
  derived from the app's actual dependencies (not a generic template) are
  set on both the API (FastAPI middleware) and the served frontend (nginx
  in production / Vite preview locally). `Strict-Transport-Security` is only
  sent when a request actually arrived over HTTPS.
- **Rate limiting**: IP-based (there is no login/user system), with
  separate, configurable limits for general traffic, search, and export
  endpoints. Health checks are exempt so uptime monitoring can't be broken
  by rate limiting.
- **Request size limits**: oversized request bodies are rejected before any
  route handling occurs.
- **Input validation**: length/range limits on search queries, patient-name
  path parameters, pagination (`limit`), and export parameters.
- **Filename sanitization**: any user-influenced value that ends up in a
  `Content-Disposition` header or generated file path is passed through an
  allow-list sanitizer (`app/utils/sanitize.py`) — this closes off both
  path-traversal and HTTP header-injection via that value.
- **Exports are generated entirely in memory** (PDF/CSV/Excel/JSON) — no
  temp files are ever written to disk, so there's nothing to accumulate or
  clean up.
- **Safe error handling**: unhandled exceptions return a generic
  `{"detail": "An internal server error occurred."}` in production
  (`DEBUG=false`) — no stack traces, SQL, file paths, or connection details
  are ever returned to the client. Full details are still logged
  server-side. Set `DEBUG=true` only for local development.
- **API docs are configurable**: `API_DOCS_ENABLED=false` disables
  `/api/docs`, `/api/redoc`, and `/api/openapi.json` entirely for
  production; they're on by default for development convenience.
- **Audit logging**: security-relevant events (patient viewed, patient
  searched, analytics requested, export generated, rate-limit exceeded,
  request errors) are logged with timestamp/IP/action/status — never with
  full record payloads, passwords, or credentials.
- **Database support**: SQLite, PostgreSQL, MySQL, and SQL Server are all
  supported through one SQLAlchemy-based connection layer, entirely
  configured via environment variables — see
  `docs/Database_Connection_Guide.pdf` for least-privilege database user
  examples and encrypted-connection configuration for each.

## Known Limitations

- The in-memory rate limiter is per-process. A multi-worker or
  multi-instance production deployment that needs strictly consistent,
  globally-shared limits should replace it with a shared store (e.g.
  Redis) — see `app/middleware/rate_limit.py`.
- A small number of transitive dependency advisories remain after this
  security pass where the fix requires a major-version upgrade (e.g.
  Starlette/cryptography/pytest) that wasn't applied blindly without the
  ability to fully regression-test it here. Run `pip-audit` /
  `npm audit` periodically and evaluate those upgrades deliberately.

## Reporting a Security Issue

If you find a security issue in this project, please report it privately
rather than opening a public GitHub issue — for example, via a private
security advisory on the repository, or directly to the maintainer. Include
enough detail to reproduce the issue. Please don't test against a
deployment containing real patient or production data.

## Recommended GitHub Repository Settings

For any fork/deployment of this repository, we recommend enabling:

- **Secret scanning** and **push protection** (blocks commits containing
  detected credentials before they land in history)
- **Dependabot alerts** and **Dependabot version updates**
- **Dependency review** on pull requests
- **Code scanning** (e.g. CodeQL)

These are GitHub repository settings, not something this codebase can turn
on for you — enable them under the repository's Settings → Code security
page.
