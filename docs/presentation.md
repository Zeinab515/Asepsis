# Asepsis: Database-Backed REST API Engine
## Technical Milestone & Defense Presentation (APIs Only)
**Project Code:** SUT-ICT-2026-ASEP  
**Track:** Track B (Backend API & Statistical Engine)  
**Deliverable:** Database-Backed FastAPI Service, Pytest Suite, README.md  
**Author:** Zeinab Ismail (Back-End Developer, ID: 250100797)  
**Academic Year:** 2026 / 2027  
**Department:** Software Engineering & Data Science / ICT, Elsewedy University of Technology (SUT)  
**Supervisors:** Dr. Rehab Farouk (Associate Prof.) & Eng. Hend Adel (Teaching Assistant)  

---

## Slide 1: Title Slide
- **Title:** Asepsis: Database-Backed REST API Engine
- **Subtitle:** High-Performance Statistical Analytics & Data Auditing APIs for Hospital Infection Control
- **Core Benchmarks:**
  - Query Latency: $< 10$ ms across dynamic multi-dimensional filters (KPI: $< 200$ ms)
  - 100% Database-Backed: Powered by PostgreSQL 16 relational tables and secured views
  - Pytest Test Suite: 30 / 30 automated tests passing in 5.06s (KPI: $\ge 25$)

---

## Slide 2: Backend Scope & Architecture
- **Headless REST API Architecture:** Completely decoupled from presentation layers.
- **Technology Stack:**
  - **FastAPI (Python 3.11+):** Asynchronous REST routing, OpenAPI 3.0 schema generation, dependency injection.
  - **SQLAlchemy 2.0 ORM:** Deterministic query layer supporting PostgreSQL 16 and SQLite.
  - **Pydantic v2:** Typed request/response validation.
  - **SciPy & NumPy:** Binomial Wilson score confidence intervals and Pearson $\chi^2$ hypothesis testing.
- **Interactive Documentation:** Live Swagger UI at `/docs` and ReDoc at `/redoc`. Root URL (`/`) redirects directly to `/docs`.

---

## Slide 3: PostgreSQL 16 Schema & Backing Views
- **Normalized Tables (7 tables):**
  - `institutions`: Facility registry.
  - `wards`: Departmental units (`Ob/Gyn`, `Paediatric`, `Medical`, `Surgical`, `NICU`).
  - `data_imports`: Immutable import ledger with SHA-256 deduplication and status check (`committed`, `archived`).
  - `hand_hygiene_opportunities`: 917 opportunities with composite unique key (`import_id + row_number`).
  - `users`: RBAC auth table (`admin`, `analyst`, `viewer`).
  - `model_runs` & `audit_log`: Model lineage and append-only user query audit trail with client IP.
- **Secured Database Views:**
  - `v_compliance_facts`: Pre-aggregates totals ($n$) and complied counts across `(ward, shift, profcat, indication)` where `status = 'committed'`. Powers sub-10ms analytical queries.
  - `v_ml_features`: Exposes only permitted predictors (`ward`, `profcat`, `shift`, `indication`, `complied`). Physically isolates leaky columns.
  - `v_import_summary`: Clean import summary view.

---

## Slide 4: Descriptive Analytics API Suite (`/api/v1/analytics`)
- `GET /api/v1/analytics/summary`
  - Query parameters: `ward`, `shift`, `profcat`, `indication`.
  - Returns: $n$, actions, rate, Wilson 95% CI $[p_{low}, p_{high}]$, institution name, and notes.
- `GET /api/v1/analytics/by-indication`
  - WHO 5 Moments breakdown + Pearson $\chi^2$ test ($p < 0.001$).
- `GET /api/v1/analytics/by-ward`
  - Ward breakdown + Pearson $\chi^2$ test ($p = 0.21$) + anti-ranking alert.
- `GET /api/v1/analytics/by-shift`
  - Shift breakdown + Pearson $\chi^2$ test ($p = 0.59$).
- `GET /api/v1/analytics/by-profcat`
  - Professional role breakdown + Pearson $\chi^2$ test ($p = 0.89$).

---

## Slide 5: Statistical Honesty in API Payloads
- **Wilson Score 95% Binomial CIs:**
  - Applied to every rate returned by the API.
  - Provides exact asymmetric bounds respecting $[0, 1]$.
  - Baseline Cohort: $22.0\%$ (95% CI: $[19.5\% - 24.8\%]$).
- **Automated Pearson $\chi^2$ Tests:**
  - Evaluates independence across groups.
  - Indication: $\chi^2 = 369.4, p < 0.001$ ➔ Significant.
  - Ward, Shift, Profession: $p \ge 0.05$ ➔ Not significant.
- **Anti-Ranking Rule:**
  - When $p \ge 0.05$, API payload includes: *"No statistically detectable difference between groups; do not rank them."*
- **Privacy & Small Samples:**
  - Rate withheld (`is_withheld: true`, `rate: null`) when $n < 5$.
  - Small sample flagged (`is_small_sample: true`) when $n < 30$.

---

## Slide 6: Data Ingestion & CSV Import API (`/api/v1/imports`)
- `POST /api/v1/imports/preview`
  - Validates CSV headers and category values.
  - Computes SHA-256 hash.
  - Scans for serial defects (`Opp #788` duplicate, `#787` missing).
  - Flags target leakage columns (`HHaction`, `Missedbutglove`).
  - Returns preview token and 5 sample rows.
- `POST /api/v1/imports/commit`
  - Enforces atomic transaction insert into `data_imports` and `hand_hygiene_opportunities`.
  - Enforces duplicate file prevention via SHA-256 unique constraint.
  - Appends record to `audit_log`.

---

## Slide 7: Target Leakage Prevention at the API Layer
- **The Threat:** `HHaction` is populated exclusively when `Complied='Yes'` and `Missedbutglove` is populated exclusively when `Complied='No'`.
- **The Guard:**
  - Both columns are barred from model inputs and API feature models.
  - View `v_ml_features` physically excludes both columns.
  - Analytical endpoints compute rates directly from raw opportunity counts, never proxy variables.

---

## Slide 8: Paginated Observation Explorer API (`/records`)
- `GET /api/v1/analytics/records`
  - Query parameters: `page`, `page_size`, `search`, `ward`, `shift`, `profcat`, `indication`.
  - True relational SQL execution: `COUNT(*)` for total records, `LIMIT` and `OFFSET` for pagination.
  - Case-insensitive search across all text attributes.
  - Sub-10ms response time.

---

## Slide 9: Audit Reports & Sanitized CSV Export API (`/reports`)
- `GET /api/v1/reports/summary`
  - Complete hospital compliance audit report with dimensions, statistical conclusion, and clinical limitations (single-hospital, Hawthorne effect, non-punitive notice).
- `GET /api/v1/reports/export-csv`
  - Streams filtered audit CSV download.
  - Formula injection defense: escapes characters (`=`, `+`, `-`, `@`) with a leading `'` to prevent DDE spreadsheet injection.

---

## Slide 10: Authentication & Security API (`/auth`)
- `POST /api/v1/auth/login`
  - Authenticates username and password against bcrypt hashes.
  - Issues signed JWT Bearer Token.
- `GET /api/v1/auth/me`
  - Returns authenticated user profile and permissions.
- **RBAC Roles:** `admin`, `analyst`, `viewer`.
- **Compliance:** Aligns with Egyptian Personal Data Protection Law No. 151/2020.

---

## Slide 11: API Latency & Performance Benchmarks
- **Measured Response Latencies:**
  - Summary API (`/analytics/summary`): **$< 4$ ms** (Proposal KPI: $< 200$ ms).
  - Group Breakdown API (`/analytics/by-ward`): **$< 7$ ms** (Proposal KPI: $< 200$ ms).
  - Pagination API (`/analytics/records`): **$< 6$ ms** (Proposal KPI: $< 200$ ms).
- **Execution Architecture:**
  - Queries indexed PostgreSQL view `v_compliance_facts`.
  - Zero flat CSV file parsing during runtime queries.

---

## Slide 12: Automated Pytest Suite & Track B Conclusion
- **Execution:** `python -m pytest backend/tests -v`
- **Result:** **30 passed in 5.06 seconds** (0 failures, 0 regressions).
- **Coverage:**
  - Database schema, views, and latency benchmarks (8 tests)
  - Descriptive analytics and chi-square calculations (10 tests)
  - Security, hashing, formula injection, and privacy (4 tests)
  - Target leakage guardrails and XAI (3 tests)
  - Clinical decision copilot tools (3 tests)
- **Track B Status: 100% Complete & Production Ready.**
