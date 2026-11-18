"""Initialize and seed PostgreSQL database for Asepsis / BIOPRESS Analytics.

Usage:
    python scripts/init_postgres.py
    python scripts/init_postgres.py --url postgresql://biopress_user:biopress_secure_pwd_2026@localhost:5432/biopress_analytics
"""
import argparse
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.security import get_password_hash
from app.db.models import HandHygieneOpportunity, User
from app.db.session import SessionLocal, init_db_and_views
from app.services.importer import commit_csv_import, preview_csv_import


def run_init_postgres(db_url: str):
    print(f"[*] Connecting to database at: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    pg_engine = create_engine(db_url, echo=False)

    # 1. Execute schema.sql
    schema_path = Path(__file__).resolve().parents[1] / "backend" / "app" / "db" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    print(f"[*] Applying PostgreSQL 16 DDL schema from {schema_path.name}...")
    schema_sql = schema_path.read_text(encoding="utf-8")

    # Split by statements or execute with raw connection
    raw_conn = pg_engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        cursor.execute(schema_sql)
        raw_conn.commit()
        cursor.close()
        print("[+] Schema, tables, constraints, indexes, and views successfully created.")
    finally:
        raw_conn.close()

    # 2. Re-initialize views and reference entities via SQLAlchemy session
    init_db_and_views(pg_engine)
    from sqlalchemy.orm import sessionmaker

    PgSession = sessionmaker(bind=pg_engine)
    db = PgSession()

    try:
        # 3. Create default users (admin, analyst, viewer)
        print("[*] Creating default authentication accounts...")
        users = [
            ("admin", "admin", "AdminPassword2026!"),
            ("analyst", "analyst", "AnalystPassword2026!"),
            ("viewer", "viewer", "ViewerPassword2026!"),
        ]
        for username, role, pwd in users:
            existing = db.query(User).filter_by(username=username).first()
            if not existing:
                u = User(
                    username=username,
                    role=role,
                    password_hash=get_password_hash(pwd),
                    is_active=True,
                )
                db.add(u)
        db.commit()
        print("[+] Users verified: admin, analyst, viewer.")

        # 4. Check if baseline data exists
        existing_count = db.query(HandHygieneOpportunity).count()
        if existing_count == 917:
            print(f"[!] Database already populated with {existing_count} opportunities.")
        else:
            raw_csv = Path(__file__).resolve().parents[1] / "data" / "raw" / "hand_hygiene_data_labeled.csv"
            print(f"[*] Ingesting and validating benchmark clinical dataset from {raw_csv.name}...")
            content = raw_csv.read_bytes()
            preview = preview_csv_import("hand_hygiene_data_labeled.csv", content)

            data_import, count = commit_csv_import(
                db=db,
                preview_token=preview.preview_token,
                imported_by="admin",
                notes="Initial verified baseline dataset (Kolola & Gezahegn, 2017).",
            )
            print(f"[+] Committed {count} opportunities into PostgreSQL under DataImport #{data_import.id}.")

        # 5. Verify integrity against views
        total = db.query(HandHygieneOpportunity).count()
        complied = db.query(HandHygieneOpportunity).filter(HandHygieneOpportunity.complied == True).count()
        facts_res = db.execute(text("SELECT SUM(n), SUM(complied_count) FROM v_compliance_facts;")).fetchone()
        facts_n = int(facts_res[0]) if facts_res else 0
        facts_k = int(facts_res[1]) if facts_res else 0

        assert total == 917, f"Expected 917 total, got {total}"
        assert complied == 202, f"Expected 202 complied, got {complied}"
        assert facts_n == 917, f"Expected 917 in v_compliance_facts, got {facts_n}"
        assert facts_k == 202, f"Expected 202 in v_compliance_facts, got {facts_k}"

        print("\n" + "=" * 60)
        print("🎉 PostgreSQL database successfully initialized and verified!")
        print(f"   - Total Opportunities: {total}")
        print(f"   - Complied Actions:    {complied}")
        print(f"   - Compliance Rate:     {round((complied / total) * 100, 1)}% (95% CI: [19.4% – 24.9%])")
        print(f"   - View v_compliance_facts: {facts_n} rows pre-aggregated")
        print("=" * 60 + "\n")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL Database for Asepsis")
    parser.add_argument(
        "--url",
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://biopress_user:biopress_secure_pwd_2026@localhost:5432/biopress_analytics",
        ),
        help="PostgreSQL connection string (default: from DATABASE_URL or localhost)",
    )
    args = parser.parse_args()
    run_init_postgres(args.url)
