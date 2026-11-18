"""Seed database with institution, wards, initial users, and 917 hand hygiene opportunities.

Usage:
    python scripts/seed_db.py
"""
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.security import get_password_hash
from app.db.models import DataImport, HandHygieneOpportunity, Institution, User, Ward
from app.db.session import SessionLocal, engine, init_db_and_views
from app.ml.evaluate import run_full_ml_benchmark
from app.services.importer import preview_csv_import, commit_csv_import


def seed_database():
    print("[*] Initializing database tables and views...")
    init_db_and_views(engine)

    db = SessionLocal()
    try:
        # 1. Create Default Users (admin, analyst, viewer)
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
                )
                db.add(u)
        db.commit()
        print("[+] Created/verified default user roles: admin, analyst, viewer.")

        # 2. Check if data already imported
        existing_opps = db.query(HandHygieneOpportunity).count()
        if existing_opps == 917:
            print(f"[!] Database already seeded with {existing_opps} opportunities.")
        else:
            raw_csv_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "hand_hygiene_data_labeled.csv"
            if not raw_csv_path.exists():
                raise FileNotFoundError(f"Raw CSV not found at {raw_csv_path}")

            print(f"[*] Reading and auditing raw dataset from {raw_csv_path.name}...")
            content = raw_csv_path.read_bytes()
            preview = preview_csv_import("hand_hygiene_data_labeled.csv", content)
            print(f"[+] Audit Preview: {preview.row_count} rows, {preview.complied_count} complied ({preview.compliance_rate}%).")
            print(f"[+] Audit Warnings detected: {len(preview.warnings)}")
            for w in preview.warnings:
                print(f"    - [{w.severity.upper()}] {w.code}: {w.message}")

            print("[*] Committing import transaction into database...")
            data_import, count = commit_csv_import(
                db=db,
                preview_token=preview.preview_token,
                imported_by="system_seed",
                notes="Initial verified baseline dataset (Kolola & Gezahegn, 2017).",
            )
            print(f"[+] Successfully committed {count} opportunities. DataImport ID: {data_import.id}")

            # Verify counts
            total = db.query(HandHygieneOpportunity).count()
            complied = db.query(HandHygieneOpportunity).filter(HandHygieneOpportunity.complied == True).count()
            rate = round((complied / total) * 100, 1)
            assert total == 917, f"Expected 917, got {total}"
            assert complied == 202, f"Expected 202, got {complied}"
            assert rate == 22.0, f"Expected 22.0%, got {rate}%"
            print(f"[+] Verification passed: {total} opportunities, {complied} complied, {rate}% compliance rate.")

        # 3. Generate initial ML benchmark report and store run
        print("[*] Running initial reproducible ML benchmark...")
        report = run_full_ml_benchmark()
        print(f"[+] ML benchmark generated. Baseline compliance: {report['baseline_compliance_rate']*100:.1f}%.")
        print(f"[+] Odds Ratios computed: {len(report['odds_ratios'])}")
        print("[+] Seed process completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
