# Asepsis (BIOPRESS Analytics Framework)
**Project Code:** SUT-ICT-2026-ASEP | **Elsewedy University of Technology (SUT)**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/pytest-30%20passed-success.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Asepsis** is a 100% software-based clinical analytics and infection prevention and control (IPC) decision support platform. Built upon the peer-reviewed clinical audit dataset from **Debre Berhan Referral Hospital (Kolola & Gezahegn, 2017)** ($n = 917$ opportunities across 5 wards), Asepsis prioritizes **statistical honesty**, automated target-leakage prevention, Wilson score confidence intervals, and explainable AI guardrails.

---

## 🏗️ Architecture & PostgreSQL Integration

### 🗄️ Relational Database Schema (`schema.sql`)
The backend is backed by an indexed, normalized PostgreSQL 16 relational database schema (with seamless SQLite fallback for local developer prototyping):
- **`institutions`**: Hospital identifier and unique name registry.
- **`wards`**: Departmental units (`Ob/Gyn`, `Paediatric`, `Medical`, `Surgical`, `NICU`) tied to institutions with unique constraints.
- **`users`**: Secure RBAC authentication table (`admin`, `analyst`, `viewer`) with bcrypt password hashes.
- **`data_imports`**: Immutable audit import log tracking file SHA-256 hashes, status (`committed`, `archived`), user attribution, and JSON diagnostic notes/warnings.
- **`hand_hygiene_opportunities`**: Audited observation records ($n = 917$) with preserved raw sequential IDs (`Opp 788` duplicated, `Opp 787` missing), strictly typed WHO categories, and composite keys (`import_id + row_number`).
- **`model_runs`**: Historical experiment tracking recording model types, Git commit hashes, feature sets, and JSON validation metrics.
- **`audit_log`**: Append-only compliance log tracking user queries, CSV imports, and administrative events with IP logging.

### 🛡️ Secured Database Views
1. **`v_ml_features`**:
   Exposes strictly permitted predictors (`ward`, `profcat`, `shift`, `indication`, `complied`) filtered by `status = 'committed'`. Completely isolates and excludes target-leaking fields (`HHaction`, `Missedbutglove`) from all ML pipelines.
2. **`v_compliance_facts`**:
   Pre-aggregated fact view across `(ward, shift, profcat, indication)` with opportunity totals ($n$) and complied counts. Enables sub-10ms analytical queries directly in SQL.
3. **`v_import_summary`**:
   Clean summary view of import transactions and warning metadata.

---

## 🌟 Backend Deliverables (Zeinab Ismail - Back-end Developer)

In accordance with **Track B (Backend API & Statistical Engine)** of the Project Proposal:
- ✅ **100% Database-Backed API**: Migrated all analytical endpoints from flat CSV reads to direct indexed SQL queries against `v_compliance_facts` and `hand_hygiene_opportunities`.
- ✅ **Sub-200 ms Query Latency**: Multi-dimensional SQL aggregations execute in $< 10$ ms across dynamic filters (Ward, Shift, Profession, Indication).
- ✅ **Statistical Honesty & Guardrails**:
  - Wilson Score 95% Binomial Confidence Intervals $[p_{low}, p_{high}]$.
  - Automated Pearson $\chi^2$ independence hypothesis testing ($p < 0.05$ flags significance; $p \ge 0.05$ enforces non-significance warnings and prohibits ranking departments).
  - Privacy Rate Withholding: rates for cohorts with $n < 5$ are automatically withheld.
  - Small-Sample Uncertainty Warnings: subgroups with $n < 30$ receive explicit sample-size warnings.
- ✅ **Robust Pytest Suite**: Expanded test coverage from 11 baseline tests to **30 passing automated tests** (exceeding the proposal KPI of $\ge 25$ tests) covering PostgreSQL schema constraints, view filters, latency benchmarks, formula injection sanitization, and ML leakage prevention.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 16 (optional for production, SQLite provided for local zero-config testing)
- Git

### 2. Installation & Setup
```bash
# Clone or navigate to the repository
cd biopress-analytics

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
#### Option A: Local SQLite (Default)
```bash
python scripts/seed_db.py
```
*Creates tables and views, sets up default roles (`admin`, `analyst`, `viewer`), audits and imports the 917 opportunities, and generates initial reproducible ML benchmarks.*

#### Option B: PostgreSQL 16
```bash
# Set connection string (or configure in .env)
export DATABASE_URL="postgresql://biopress_user:biopress_secure_pwd_2026@localhost:5432/biopress_analytics"

# Run PostgreSQL automated DDL and seed script
python scripts/init_postgres.py
```

### 4. Run Automated Pytest Suite
```bash
python -m pytest backend/tests -v
```
*Executes all 30 tests verifying statistical calculations, DB views, leakage guardrails, and API endpoints.*

### 5. Launch the FastAPI Backend
```bash
cd backend
uvicorn app.main:app --reload
```
- **Web Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐳 Docker Production Deployment

To run the complete production stack (PostgreSQL 16 container + FastAPI backend):
```bash
docker compose up --build
```
The application will be live at `http://localhost:8000`.

---

## 📜 Ethical & Clinical Governance Notice

> [!IMPORTANT]
> **Mandatory Observational Audit Disclosure:**
> - Data originates from a single hospital observational audit (Debre Berhan, Ethiopia, 2017). Direct human observation is subject to the Hawthorne effect (temporarily elevated compliance).
> - Results describe systemic opportunities and WHO clinical contact moments.
> - **Non-Disciplinary Policy**: Audit findings and model estimates **MUST NEVER** be used to rank, evaluate, or discipline individual healthcare workers. Differences describe observational correlations, never direct causes.
