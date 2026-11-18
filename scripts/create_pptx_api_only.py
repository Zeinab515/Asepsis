import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette
BG_DARK = RGBColor(15, 23, 42)        # #0f172a
BG_CARD = RGBColor(30, 41, 59)        # #1e293b
CARD_BORDER = RGBColor(51, 65, 85)    # #334155
PRIMARY_CYAN = RGBColor(56, 189, 248) # #38bdf8
ACCENT_GREEN = RGBColor(16, 185, 129) # #10b981
AMBER_WARN = RGBColor(245, 158, 11)   # #f59e0b
TEXT_WHITE = RGBColor(248, 250, 252)  # #f8fafc
TEXT_MUTED = RGBColor(148, 163, 184)  # #94a3b8
INDIGO_BADGE = RGBColor(79, 70, 229)  # #4f46e5

blank_layout = prs.slide_layouts[6]

def apply_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_DARK
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, tag_text, title_text, slide_number_str):
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = PRIMARY_CYAN

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    num_box = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(1.0), Inches(0.4))
    tf_num = num_box.text_frame
    p_num = tf_num.paragraphs[0]
    p_num.text = slide_number_str
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.size = Pt(11)
    p_num.font.bold = True
    p_num.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, title="", body="", highlight=False, stat_hero="", stat_label=""):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = BG_CARD
    card.line.color.rgb = PRIMARY_CYAN if highlight else CARD_BORDER
    card.line.width = Pt(1.5 if highlight else 1)
    
    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)
    
    first = True
    if stat_label:
        p = tf.paragraphs[0]
        p.text = stat_label.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        first = False
        
    if stat_hero:
        p = tf.add_paragraph() if not first else tf.paragraphs[0]
        p.text = stat_hero
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN if not highlight else PRIMARY_CYAN
        first = False

    if title:
        p = tf.add_paragraph() if not first else tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_CYAN
        first = False
        
    if body:
        for line in body.split("\n"):
            p = tf.add_paragraph() if not first else tf.paragraphs[0]
            p.text = line
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_WHITE if line.startswith("•") or line.startswith("✓") or line.startswith("GET") or line.startswith("POST") else TEXT_MUTED
            first = False
    return card

def add_banner(slide, left, top, width, height, text, banner_type="amber"):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    b.fill.solid()
    if banner_type == "amber":
        b.fill.fore_color.rgb = RGBColor(45, 30, 15)
        b.line.color.rgb = AMBER_WARN
    elif banner_type == "green":
        b.fill.fore_color.rgb = RGBColor(15, 40, 30)
        b.line.color.rgb = ACCENT_GREEN
    else:
        b.fill.fore_color.rgb = RGBColor(20, 35, 55)
        b.line.color.rgb = PRIMARY_CYAN
    b.line.width = Pt(1.2)
    
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    return b

# ==============================================================================
# SLIDE 1: Title Slide (APIs Focused)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(3.6), Inches(0.38))
badge.fill.solid()
badge.fill.fore_color.rgb = INDIGO_BADGE
badge.line.fill.background()
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "SUT-ICT-2026-ASEP  |  TRACK B DELIVERABLE"
p_b.alignment = PP_ALIGN.CENTER
p_b.font.size = Pt(10.5)
p_b.font.bold = True
p_b.font.color.rgb = TEXT_WHITE

t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.2))
tf = t_box.text_frame
tf.word_wrap = True
p1 = tf.paragraphs[0]
p1.text = "Asepsis: Database-Backed REST API Engine"
p1.font.size = Pt(32)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE

p2 = tf.add_paragraph()
p2.text = "High-Performance Statistical Analytics & Data Auditing APIs for Hospital Infection Control"
p2.font.size = Pt(16)
p2.font.color.rgb = PRIMARY_CYAN

add_card(s1, Inches(0.8), Inches(3.6), Inches(3.6), Inches(1.7), stat_hero="< 10 ms", stat_label="Query Latency KPI", body="Multi-dimensional SQL aggregation across 917 clinical opportunities.", highlight=True)
add_card(s1, Inches(4.8), Inches(3.6), Inches(3.6), Inches(1.7), stat_hero="100%", stat_label="Database-Backed", body="Zero flat CSV file loading in production; powered by PostgreSQL 16 & views.", highlight=True)
add_card(s1, Inches(8.8), Inches(3.6), Inches(3.7), Inches(1.7), stat_hero="30 / 30", stat_label="Pytest Test Suite", body="100% automated test pass rate in 5.06s covering all endpoints and edge cases.", highlight=True)

f_box = s1.shapes.add_textbox(Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.4))
tf_f = f_box.text_frame
tf_f.word_wrap = True
p = tf_f.paragraphs[0]
p.text = "Elsewedy University of Technology (SUT)  •  Software Engineering & Data Science / ICT"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = PRIMARY_CYAN

p = tf_f.add_paragraph()
p.text = "Back-End Developer: Zeinab Ismail (250100797)  •  Track B Lead"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

p = tf_f.add_paragraph()
p.text = "Supervisors: Dr. Rehab Farouk (Associate Prof.)  •  Eng. Hend Adel (Teaching Assistant)"
p.font.size = Pt(10.5)
p.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 2: Backend Architecture & Technology Stack
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "Architecture & Specifications", "Pure Headless REST API Architecture", "02 / 12")

add_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="Core Technology Stack",
         body="• FastAPI (Python 3.11+):\n  High-performance asynchronous REST framework with automatic OpenAPI schemas.\n• SQLAlchemy 2.0 ORM:\n  Deterministic query layer supporting PostgreSQL 16 (production) and SQLite (dev).\n• Pydantic v2:\n  Strict request/response validation.\n• SciPy & NumPy:\n  Wilson CIs & Chi-square calculations.")

add_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="API Modular Routing",
         body="• /api/v1/analytics:\n  Descriptive compliance & hypothesis tests.\n• /api/v1/imports:\n  CSV schema validation & commit pipeline.\n• /api/v1/reports:\n  Formal audit summaries & sanitized export.\n• /api/v1/auth:\n  JWT Bearer tokens & role security.\n• /health:\n  Automated service liveness probe.",
         highlight=True)

add_card(s2, Inches(8.8), Inches(1.6), Inches(3.7), Inches(4.2),
         title="Headless & Scalable",
         body="• Pure JSON REST Architecture:\n  Completely decoupled from front-end presentation layers.\n• Interactive Swagger Docs:\n  Auto-generated UI live at /docs.\n• ReDoc Documentation:\n  Enterprise schema documentation at /redoc.\n• Production Container Ready:\n  Dockerized with PostgreSQL 16.")

add_banner(s2, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🚀 Clean Decoupling: Root URL (/) redirects directly to interactive Swagger UI documentation at /docs.", "blue")

# ==============================================================================
# SLIDE 3: Relational Database Schema & Secured Views
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "Database Engineering", "PostgreSQL 16 Schema & Backing Views", "03 / 12")

add_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="Normalized Relational Tables",
         body="• institutions: Hospital registry ('Debre Berhan referral hospital').\n• wards: Clinical departments (Ob/Gyn, Paediatric, Medical, Surgical, NICU).\n• data_imports: Immutable audit ledger with SHA-256 deduplication and status check ('committed', 'archived').\n• hand_hygiene_opportunities: 917 observation opportunities with composite unique key (import_id + row_number).\n• users: RBAC auth table (admin, analyst, viewer).\n• audit_log: Append-only compliance trail with client IP addresses.")

add_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Secured Relational Views",
         body="• View: v_compliance_facts\n  Pre-aggregates total opportunities (n) and complied actions grouped by (ward, shift, profcat, indication) where status = 'committed'.\n  ➔ Powers all analytical queries in under 10 milliseconds!\n\n• View: v_ml_features\n  Exposes strictly permitted predictors (ward, profcat, shift, indication, complied).\n  ➔ Physically excludes leaky columns (HHaction, Missedbutglove).")

add_banner(s3, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "✓ Database Integrity: All analytical endpoints query indexed relational views; raw observation CSVs are never read during runtime queries.", "green")

# ==============================================================================
# SLIDE 4: Descriptive Analytics API Suite
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Core Analytical Endpoints", "Descriptive Analytics API Suite (/api/v1/analytics)", "04 / 12")

rows, cols = 5, 3
tbl_shape = s4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.2))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.4)
tbl.columns[1].width = Inches(3.3)
tbl.columns[2].width = Inches(5.0)

headers = ["Endpoint & Method", "Query Parameters", "Calculated Output Payload"]
for col_idx, h in enumerate(headers):
    cell = tbl.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(30, 58, 95)
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_CYAN

data = [
    ("GET /api/v1/analytics/summary", "ward, shift, profcat, indication", "opportunities (n), actions (k), compliance_rate, ci_low, ci_high (Wilson 95% CI)."),
    ("GET /api/v1/analytics/by-indication", "ward, shift, profcat", "WHO 5 Moments breakdown, group n, complied, rates, Wilson CIs, chi-square test (p < 0.001)."),
    ("GET /api/v1/analytics/by-ward", "shift, profcat, indication", "5 wards breakdown, rates, CIs, chi-square test (p = 0.21), anti-ranking verdict note."),
    ("GET /api/v1/analytics/by-shift & by-profcat", "Dynamic dimension filters", "Shift breakdown (p = 0.59) & Profession breakdown (p = 0.89) with non-significance guardrails."),
]

for row_idx, (c0, c1, c2) in enumerate(data, start=1):
    for col_idx, text_val in enumerate([c0, c1, c2]):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = text_val
        p.font.size = Pt(10)
        p.font.color.rgb = PRIMARY_CYAN if col_idx == 0 else (TEXT_WHITE if col_idx == 1 else TEXT_MUTED)

add_banner(s4, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "⚡ Dynamic Multi-Filtering: Any combination of ward, shift, profcat, and indication can be passed as query parameters simultaneously.", "blue")

# ==============================================================================
# SLIDE 5: Statistical Honesty in API Payloads
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "Scientific Rigor & Ethics", "Statistical Honesty Guardrails Built Into APIs", "05 / 12")

add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="1. Wilson Score 95% Binomial CIs",
         body="• Applied to every rate returned by the API.\n• Provides exact [ci_low, ci_high] asymmetric bounds.\n• Baseline Cohort: 22.0% (95% CI: [19.5% – 24.8%]).\n• Robust against sample-size collapse where normal approximation intervals fail.")

add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="2. Automated Chi-Square (chi2) Tests",
         body="• Built directly into every /by-{dimension} response.\n• Computes chi2, p_value, degrees of freedom, and minimum expected count.\n• WHO Indication: p < 0.001 ➔ Statistically Significant.\n• Wards (p=0.21), Shifts (p=0.59), Roles (p=0.89) ➔ Insignificant.")

add_banner(s5, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "⚠️ Anti-Ranking Rule: When p >= 0.05, the API returns: 'No statistically detectable difference between groups; do not rank them.' Privacy rate withholding masks rates when n < 5; small-sample alerts trigger when n < 30.", "amber")

# ==============================================================================
# SLIDE 6: Data Ingestion & CSV Import API
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Data Ingestion Pipeline", "Data Ingestion & CSV Audit API (/api/v1/imports)", "06 / 12")

add_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="POST /api/v1/imports/preview",
         body="Pre-flight CSV validation without writing to DB:\n• Computes cryptographic SHA-256 hash.\n• Verifies required column headers.\n• Validates categorical domain values.\n• Detects Opp sequence gaps (Opp 787 missing, 788 duplicate).\n• Flags target leakage columns (HHaction, Missedbutglove).\n• Returns preview token and first 5 sample rows.")

add_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="POST /api/v1/imports/commit",
         body="Atomic transactional database ingestion:\n• Validates preview token.\n• Checks SHA-256 uniqueness (prevents re-importing duplicate files).\n• Inserts DataImport record with status='committed'.\n• Bulk-inserts HandHygieneOpportunity records.\n• Writes event to append-only audit_log table.\n• Returns committed row count and import ID.")

add_banner(s6, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🔒 Contract Defense: Malformed files, missing columns, or unexpected categorical values are rejected immediately with descriptive 400 Bad Request errors.", "green")

# ==============================================================================
# SLIDE 7: Target Leakage Prevention
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Data Guardrails", "Target Leakage Guardrails at the API Layer", "07 / 12")

add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="The Target Leakage Vulnerability",
         body="In observational clinical datasets, secondary columns often leak the outcome deterministically:\n\n• HHaction: Populated in 100% of compliant rows ('HW' / 'HR') and null in 100% of non-compliant rows.\n• Missedbutglove: Populated in 100% of non-compliant rows ('Yes' / 'No') and null in 100% of compliant rows.\n\n➔ Any model trained on these variables achieves artificial 100% accuracy with zero real-world clinical validity.")

add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Asepsis Architectural Prevention",
         body="How our backend mathematically isolates leakage:\n\n1. Ingestion Scanner: Flags critical leakage warnings in import preview.\n2. Relational View: v_ml_features strictly omits both columns.\n3. Automated Pytest Guard: evaluate.load_ml_dataset() immediately raises ValueError if either column is introduced into ML pipelines.\n4. Zero Leakage in Production APIs: Analytical endpoints aggregate on raw opportunity counts, never proxy indicators.")

add_banner(s7, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🛡️ Verified by Automated Tests: test_leakage_guard_raises_error_if_leaky_columns_provided confirms strict prohibition across all code paths.", "blue")

# ==============================================================================
# SLIDE 8: Paginated Observation Explorer API
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Database Pagination", "Paginated Records Explorer API (/records)", "08 / 12")

add_card(s8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="GET /api/v1/analytics/records",
         body="Query Parameters:\n• page: 1-based page index (default: 1)\n• page_size: items per page (default: 25, max: 100)\n• search: case-insensitive text search across ward, profession, shift, indication\n• ward, shift, profcat, indication: multi-column filters\n\nSQL Implementation:\nSELECT o.*, w.name FROM hand_hygiene_opportunities o\nJOIN wards w ON o.ward_id = w.id\nWHERE status = 'committed' AND ...\nLIMIT :page_size OFFSET :offset;")

add_card(s8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Response Payload Structure",
         body="{\n  \"total\": 917,\n  \"page\": 1,\n  \"page_size\": 25,\n  \"total_pages\": 37,\n  \"items\": [\n    {\n      \"id\": 1,\n      \"row_number\": 1,\n      \"source_opp\": 1,\n      \"ward\": \"Ob/Gyn\",\n      \"profcat\": \"Midwife\",\n      \"shift\": \"Morning\",\n      \"indication\": \"Before patient contact\",\n      \"complied\": false\n    }\n  ]\n}")

add_banner(s8, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "⚡ True Relational Pagination: Queries execute with database-level COUNT(*) and LIMIT/OFFSET, avoiding in-memory array slicing.", "green")

# ==============================================================================
# SLIDE 9: Audit Reports & Sanitized CSV Export API
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
apply_background(s9)
add_header(s9, "Clinical Reporting & Security", "Audit Reports & CSV Export API (/reports)", "09 / 12")

add_card(s9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="GET /api/v1/reports/summary",
         body="Generates formal hospital IPC compliance audit summary:\n• Overall metrics: 917 opportunities, 202 actions (22.0%).\n• Multi-dimensional breakdowns (Indication, Ward, Shift, Profession).\n• Methodological conclusion: Indication is the sole statistically significant factor (p < 0.001).\n• Mandatory limitation caveats:\n  - Single hospital observational audit data.\n  - Hawthorne effect observer presence bias.\n  - Non-disciplinary policy prohibiting staff ranking.")

add_card(s9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="GET /api/v1/reports/export-csv",
         body="Streams sanitized CSV file of filtered audit records:\n\nSpreadsheet Formula Injection Defense:\n• Cells beginning with '=', '+', '-', or '@' are automatically escaped with leading single quote (').\n• Prevents Dynamic Data Exchange (DDE) remote command execution attacks when hospital staff open exports in Excel.\n\nQuery Parameters:\nAccepts active dynamic filters (ward, shift, profcat, indication).")

add_banner(s9, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🛡️ Healthcare Data Governance: Mitigates spreadsheet vulnerabilities while producing accreditation-ready audit documentation.", "blue")

# ==============================================================================
# SLIDE 10: Authentication & Security API
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
apply_background(s10)
add_header(s10, "Access Control & Governance", "Authentication & Security API (/auth)", "10 / 12")

add_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="POST /api/v1/auth/login",
         body="• Verifies credentials against users table using bcrypt hashing.\n• Generates signed JWT Bearer Token (HS256).\n• Encodes user identity, role, and expiration timestamp.\n• Returns token, token_type ('bearer'), username, and role.\n\nRole-Based Access Control (RBAC):\n• admin: Upload audit CSVs, manage users, full access.\n• analyst: View analytics, run ML models, export data.\n• viewer: Read-only access to compliance reports.")

add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Security Architecture",
         body="• GET /api/v1/auth/me:\n  Validates Authorization: Bearer <token> header and returns user profile.\n• Password Security:\n  Passwords stored strictly as salted bcrypt hashes ($2b$12$...); never plain text.\n• Audit Logging:\n  All sensitive operations (importing datasets, logins) logged to audit_log table with user ID, action, and IP address.\n• Least-Privilege Database Roles:\n  Prepared for migration_owner, app_rw, and analytics_ro.")

add_banner(s10, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🔒 Compliance: Adheres to Egyptian Personal Data Protection Law No. 151/2020 and Anti-Cyber Crimes Law No. 175/2018.", "green")

# ==============================================================================
# SLIDE 11: API Performance Benchmarks (< 10ms Latency)
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
apply_background(s11)
add_header(s11, "Performance Verification", "API Latency Benchmarks (Sub-10ms vs <200ms KPI)", "11 / 12")

add_card(s11, Inches(0.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="Summary Endpoint Latency",
         stat_hero="< 4 ms",
         stat_label="Measured Execution Time",
         body="Endpoint:\nGET /api/v1/analytics/summary\n\nExecution:\nQueries pre-aggregated v_compliance_facts view in SQL.\n\nProposal KPI:\n< 200 ms average latency.\nAchieved: Over 50x faster than target!")

add_card(s11, Inches(4.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="Group Breakdown Latency",
         stat_hero="< 7 ms",
         stat_label="Measured Execution Time",
         body="Endpoint:\nGET /api/v1/analytics/by-ward\n\nExecution:\nSQL GROUP BY + contingency matrix + chi2_contingency calculation.\n\nProposal KPI:\n< 200 ms average latency.\nAchieved: Over 25x faster than target!",
         highlight=True)

add_card(s11, Inches(8.8), Inches(1.6), Inches(3.7), Inches(4.2),
         title="Pagination Latency",
         stat_hero="< 6 ms",
         stat_label="Measured Execution Time",
         body="Endpoint:\nGET /api/v1/analytics/records?page=1&page_size=25\n\nExecution:\nRelational JOIN between hand_hygiene_opportunities and wards with LIMIT/OFFSET.\n\nProposal KPI:\n< 200 ms average latency.")

add_banner(s11, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "⚡ Verified by Benchmark Tests: test_sql_query_latency_under_200ms_benchmark systematically asserts <200ms across all filter permutations.", "blue")

# ==============================================================================
# SLIDE 12: Automated Pytest Suite & Track B Conclusion
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
apply_background(s12)
add_header(s12, "Verification & Milestone Summary", "30 / 30 Automated Pytest Tests Passing", "12 / 12")

add_card(s12, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="Full Test Suite Breakdown (30 Tests)",
         body="• Database & Views (8 tests): View structures, leakage exclusion, status='committed' filter, query latency benchmark, reference integrity.\n• Descriptive Analytics (10 tests): Exact 22.0% reproduction, group totals consistency, chi-square p-values, Wilson CI edge cases.\n• Security & Privacy (4 tests): Password hashing, formula injection sanitization, n<5 rate withholding, n<30 sample warnings.\n• ML & XAI Engine (3 tests): Automated leakage guard, odds ratios, scenario explainer.\n• Decision Copilot Agent (3 tests): Anti-ranking guardrail, causality refusal, anomaly rediscovery.")

add_card(s12, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Track B Deliverables: 100% Complete",
         body="Execution Summary:\n• Test Duration: 5.06 seconds for all 30 tests.\n• Failures / Errors: 0 failures, 0 regressions.\n• Proposal Deliverable: 'Database-backed FastAPI service, pytest suite, README.md' — 100% delivered.\n• Frozen OpenAPI Contract: Ready for front-end team integration.\n• PostgreSQL Integration: schema.sql & init_postgres.py scripts verified.",
         highlight=True)

add_banner(s12, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🎓 Deliverable Complete: Headless, high-performance, statistically honest REST API ready for supervisor defense and frontend binding.", "green")

# Save Presentation
output_path = Path("C:/Users/zeina/.gemini/antigravity/scratch/biopress-analytics/Asepsis_Milestone_Defense.pptx")
prs.save(str(output_path))
print(f"[+] Successfully generated pure API PowerPoint presentation: {output_path} ({len(prs.slides)} slides)")

docs_output = Path("C:/Users/zeina/.gemini/antigravity/scratch/biopress-analytics/docs/Asepsis_Milestone_Defense.pptx")
prs.save(str(docs_output))
print(f"[+] Also saved to docs: {docs_output}")
