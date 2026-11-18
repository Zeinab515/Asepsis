"""SQLAlchemy models for Asepsis / BIOPRESS Analytics.

Ground rules & Design decisions (docs/architecture.md & team plans):
- Exactly matches PostgreSQL 16 schema (schema.sql).
- Preserves raw source_opp as-is (Opp 788 is duplicated, Opp 787 missing).
- Unique key: row_number + import_id.
- No invented date, worker_id, or session_id columns because raw data has none.
- CHECK constraints on allowed categorical values and complied is not null.
- Target leakage columns (hh_action, missed_but_glove) are nullable in storage
  but strictly excluded from v_ml_features and all ML training paths.
"""
import json
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)

    wards = relationship("Ward", back_populates="institution", cascade="all, delete-orphan")


class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    institution = relationship("Institution", back_populates="wards")
    opportunities = relationship("HandHygieneOpportunity", back_populates="ward")

    __table_args__ = (
        UniqueConstraint("institution_id", "name", name="uq_wards_institution_name"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'analyst', 'viewer')", name="ck_users_role"),
    )


class DataImport(Base):
    __tablename__ = "data_imports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False, unique=True)
    row_count = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="committed")  # 'committed', 'archived'
    imported_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)  # JSON text: import warnings & user notes

    user = relationship("User", foreign_keys=[imported_by])
    opportunities = relationship("HandHygieneOpportunity", back_populates="data_import", cascade="all, delete-orphan")
    model_runs = relationship("ModelRun", back_populates="data_import")

    __table_args__ = (
        CheckConstraint("status IN ('committed', 'archived')", name="ck_data_imports_status"),
        CheckConstraint("row_count >= 0", name="ck_data_imports_row_count"),
    )

    @property
    def warnings(self) -> str:
        """Extract warnings JSON array from notes for backwards-compatible consumers."""
        if self.notes:
            try:
                parsed = json.loads(self.notes)
                if isinstance(parsed, dict) and "warnings" in parsed:
                    return json.dumps(parsed["warnings"])
                if isinstance(parsed, list):
                    return self.notes
            except Exception:
                pass
        return "[]"


class HandHygieneOpportunity(Base):
    __tablename__ = "hand_hygiene_opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_id = Column(Integer, ForeignKey("data_imports.id", ondelete="RESTRICT"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    source_opp = Column(Integer, nullable=True)  # Preserved as-is (e.g. 788 appears twice, 787 missing)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False, index=True)
    profcat = Column(String(50), nullable=False)
    shift = Column(String(50), nullable=False, index=True)
    indication = Column(String(100), nullable=False, index=True)
    hh_action = Column(String(50), nullable=True)  # LEAKY: never a model input
    missed_but_glove = Column(String(10), nullable=True)  # LEAKY: never a model input
    complied = Column(Boolean, nullable=False)

    data_import = relationship("DataImport", back_populates="opportunities")
    ward = relationship("Ward", back_populates="opportunities")

    __table_args__ = (
        UniqueConstraint("import_id", "row_number", name="uq_opportunity_import_row"),
        CheckConstraint("profcat IN ('Nurse', 'Medical doctor', 'Midwife', 'Other')", name="ck_opp_profcat"),
        CheckConstraint("shift IN ('Morning', 'After noon', 'Night')", name="ck_opp_shift"),
        CheckConstraint(
            "indication IN ('Before patient contact', 'Before an aseptic procedure', 'After patient contact', 'After contact with patient Surroundings', 'After body fluid exposure')",
            name="ck_opp_indication",
        ),
        CheckConstraint("hh_action IS NULL OR hh_action IN ('HW (hand wash)', 'HR (hand rub)')", name="ck_opp_hh_action"),
        CheckConstraint("missed_but_glove IS NULL OR missed_but_glove IN ('Yes', 'No')", name="ck_opp_missed"),
        CheckConstraint("complied IS NOT NULL", name="ck_opp_complied_not_null"),
    )


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    model_type = Column(String(50), nullable=False)
    git_commit = Column(String(40), nullable=True)
    data_import_id = Column(Integer, ForeignKey("data_imports.id"), nullable=True)
    features = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)
    artifact_path = Column(String(500), nullable=True)

    data_import = relationship("DataImport", back_populates="model_runs")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username = Column(String(64), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    resource = Column(String(200), nullable=True)
    details = Column(JSON, nullable=True)
    ip = Column(String(45), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    @property
    def timestamp(self):
        """Backwards compatibility alias for ts."""
        return self.ts
