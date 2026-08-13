"""
Seed the configured SQL database with a realistic, synthetic dummy dataset.

This is the "make me a dummy database" script: point `DATABASE_URL` (or the
individual `DB_*` variables) in `backend/.env` at any SQLite, PostgreSQL, or
MySQL database and run:

    python -m scripts.seed_dummy_data

It creates the `patient_visits` table if missing and inserts synthetic
patient visit records (deterministic, seeded — same data every run unless
you change --seed). Safe to re-run: pass --reset to wipe existing rows
first, otherwise records are appended (deduplicated by record_id).

Examples
--------
Seed the database configured in .env with the default 550 records:
    python -m scripts.seed_dummy_data

Wipe and reseed with 2,000 records:
    python -m scripts.seed_dummy_data --reset --count 2000
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import random
import sys
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.config import get_settings
from app.db.session import Base, SessionLocal, check_database_connection, engine
from app.db.models import PatientVisit
from app.services.cors_service import ensure_default_origins

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("patient360.seed")

FIRST_NAMES = [
    "Ali", "Fatima", "Ahmed", "Ayesha", "Bilal", "Sana", "Usman", "Hina", "Omar", "Zara",
    "Hassan", "Mariam", "Kashif", "Nida", "Saad", "Rabia", "Imran", "Sadia", "Tariq", "Amna",
]
LAST_NAMES = ["Saleem", "Khan", "Malik", "Butt", "Raza", "Iqbal", "Farooq", "Sheikh", "Chaudhry", "Aslam"]
HOSPITALS = [
    "National Hospital", "Aga Khan University Hospital", "Liaquat National Hospital",
    "Shifa International", "South City Hospital", "Ziauddin Hospital", "Indus Hospital",
]
DOCTORS = [
    "Dr Ahmed", "Dr Fatima Noor", "Dr Bilal Hussain", "Dr Sana Malik", "Dr Usman Tariq",
    "Dr Ayesha Raza", "Dr Kashif Iqbal",
]
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan"]
DISEASES = [
    "Diabetes", "Hypertension", "Kidney Disease", "Asthma", "Heart Disease", "Migraine",
    "Arthritis", "Thyroid Disorder", "Anemia", "Obesity", "Allergy", "Bronchitis", "Gastritis",
]
NOTES_OPTIONS = ["Routine checkup", "Follow-up visit", "Emergency admission", "Lab tests ordered", None]


def _random_date(rng: random.Random) -> date:
    start = date(2021, 1, 1)
    end = date(2025, 12, 31)
    return start + timedelta(days=rng.randint(0, (end - start).days))


def _make_record_id(batch_label: str, index: int, patient_name: str, visit_date: date, hospital: str) -> str:
    raw = f"{batch_label}|{index}|{patient_name}|{visit_date}|{hospital}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def generate_dummy_rows(count: int, seed: int = 42, batch_label: str = "dummy_seed") -> list[dict]:
    """Generate `count` synthetic patient visit rows, deterministic for a given seed."""
    rng = random.Random(seed)
    patients = [f"{f} {l}" for f in FIRST_NAMES for l in LAST_NAMES]
    rng.shuffle(patients)
    patients = patients[: min(80, len(patients))]

    rows = []
    for i in range(count):
        patient_name = rng.choice(patients)
        visit_date = _random_date(rng)
        hospital = rng.choice(HOSPITALS)
        rows.append(
            {
                "record_id": _make_record_id(batch_label, i, patient_name, visit_date, hospital),
                "patient_name": patient_name,
                "visit_date": visit_date,
                "hospital": hospital,
                "doctor": rng.choice(DOCTORS),
                "city": rng.choice(CITIES),
                "diseases": rng.sample(DISEASES, rng.randint(1, 3)),
                "claim_amount": round(rng.uniform(1500, 45000), 2),
                "notes": rng.choice(NOTES_OPTIONS),
                "source_file": batch_label,
            }
        )
    return rows


def _upsert_statement(rows: list[dict]):
    """Build a dialect-appropriate INSERT ... ON CONFLICT DO NOTHING statement."""
    url = get_settings().sqlalchemy_database_url
    if url.startswith("sqlite"):
        stmt = sqlite_insert(PatientVisit).values(rows)
        return stmt.on_conflict_do_nothing(index_elements=["record_id"])
    if url.startswith("postgresql"):
        stmt = pg_insert(PatientVisit).values(rows)
        return stmt.on_conflict_do_nothing(index_elements=["record_id"])
    if url.startswith("mysql"):
        stmt = mysql_insert(PatientVisit).values(rows)
        return stmt.on_duplicate_key_update(record_id=stmt.inserted.record_id)
    # Fallback for any other SQLAlchemy-supported dialect: plain insert
    # (may raise on duplicate record_id, which is fine for a fresh DB).
    return PatientVisit.__table__.insert().values(rows)


def seed(count: int = 550, seed_value: int = 42, reset: bool = False, batch_size: int = 200) -> None:
    settings = get_settings()

    connected, message = check_database_connection()
    if not connected:
        logger.error("Cannot connect to the configured database: %s", message)
        logger.error("Check DATABASE_URL / DB_* values in backend/.env, then try again.")
        sys.exit(1)

    logger.info("Connected via %s driver.", settings.resolved_driver_name)

    Base.metadata.create_all(bind=engine)
    logger.info("Schema ensured (patient_visits table present).")

    ensure_default_origins()
    logger.info("Default allowed CORS origins ensured (if the table was empty).")

    with SessionLocal() as db:
        if reset:
            deleted = db.execute(delete(PatientVisit))
            db.commit()
            logger.info("Cleared existing rows (--reset was passed).")

        rows = generate_dummy_rows(count, seed=seed_value)
        inserted = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            db.execute(_upsert_statement(batch))
            db.commit()
            inserted += len(batch)
            logger.info("Inserted %s/%s rows...", inserted, len(rows))

        total = db.execute(select(PatientVisit.id)).all()
        logger.info("Done. Table now has %s total row(s).", len(total))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Patient 360 database with dummy data.")
    parser.add_argument("--count", type=int, default=550, help="Number of visit records to generate.")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (deterministic output).")
    parser.add_argument("--reset", action="store_true", help="Delete all existing rows before seeding.")
    args = parser.parse_args()

    seed(count=args.count, seed_value=args.seed, reset=args.reset)


if __name__ == "__main__":
    main()
