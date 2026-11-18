import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Institution, Ward

# Default to SQLite local database file inside data/ directory for development/testing
DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "biopress.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# For SQLite, enable check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db_and_views(target_engine=engine):
    """Create all tables and the secured views v_ml_features, v_compliance_facts, and v_import_summary.
    Also ensures base reference institution and wards exist.
    """
    Base.metadata.create_all(bind=target_engine)

    with target_engine.connect() as conn:
        # View 1: v_ml_features
        # Strictly exposes only: ward, profcat, shift, indication, complied.
        # NEVER exposes hh_action or missed_but_glove to completely prevent target leakage!
        # Filters WHERE i.status = 'committed'
        conn.execute(text("DROP VIEW IF EXISTS v_ml_features;"))
        conn.execute(
            text(
                """
            CREATE VIEW v_ml_features AS
            SELECT w.name AS ward,
                   o.profcat AS profcat,
                   o.shift AS shift,
                   o.indication AS indication,
                   o.complied AS complied
            FROM hand_hygiene_opportunities o
            JOIN wards w ON w.id = o.ward_id
            JOIN data_imports i ON i.id = o.import_id
            WHERE i.status = 'committed';
        """
            )
        )

        # View 2: v_compliance_facts
        # Aggregated facts across standard dimensions for fast analytics
        # Filters WHERE i.status = 'committed'
        conn.execute(text("DROP VIEW IF EXISTS v_compliance_facts;"))
        conn.execute(
            text(
                """
            CREATE VIEW v_compliance_facts AS
            SELECT w.name AS ward,
                   o.shift AS shift,
                   o.profcat AS profcat,
                   o.indication AS indication,
                   COUNT(*) AS n,
                   SUM(CASE WHEN o.complied THEN 1 ELSE 0 END) AS complied_count
            FROM hand_hygiene_opportunities o
            JOIN wards w ON w.id = o.ward_id
            JOIN data_imports i ON i.id = o.import_id
            WHERE i.status = 'committed'
            GROUP BY w.name, o.shift, o.profcat, o.indication;
        """
            )
        )

        # View 3: v_import_summary
        conn.execute(text("DROP VIEW IF EXISTS v_import_summary;"))
        conn.execute(
            text(
                """
            CREATE VIEW v_import_summary AS
            SELECT id, filename, sha256, row_count, status, imported_at, notes
            FROM data_imports;
        """
            )
        )
        conn.commit()

    # Pre-populate reference data if not present
    session = sessionmaker(bind=target_engine)()
    try:
        inst = session.query(Institution).filter(
            (Institution.id == 1) | (Institution.name == "Debre Berhan referral hospital")
        ).first()
        if not inst:
            inst = Institution(name="Debre Berhan referral hospital")
            session.add(inst)
            session.flush()

        default_wards = ["Ob/Gyn", "Paediatric", "Medical", "Surgical", "NICU"]
        for ward_name in default_wards:
            w = session.query(Ward).filter_by(institution_id=inst.id, name=ward_name).first()
            if not w:
                session.add(Ward(institution_id=inst.id, name=ward_name))
        session.commit()
    except Exception as e:
        session.rollback()
        # Non-fatal if already present or concurrently seeded
        pass
    finally:
        session.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
