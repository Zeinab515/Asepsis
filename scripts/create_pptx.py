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
BG_DARK = RGBColor(15, 23, 42)       # #0f172a
BG_CARD = RGBColor(30, 41, 59)       # #1e293b
CARD_BORDER = RGBColor(51, 65, 85)   # #334155
PRIMARY_CYAN = RGBColor(56, 189, 248)# #38bdf8
ACCENT_GREEN = RGBColor(16, 185, 129)# #10b981
AMBER_WARN = RGBColor(245, 158, 11)  # #f59e0b
TEXT_WHITE = RGBColor(248, 250, 252) # #f8fafc
TEXT_MUTED = RGBColor(148, 163, 184) # #94a3b8
TEXT_DARK = RGBColor(15, 23, 42)
INDIGO_BADGE = RGBColor(79, 70, 229) # #4f46e5

blank_layout = prs.slide_layouts[6]

def apply_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_DARK
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, tag_text, title_text, slide_number_str):
    # Tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = PRIMARY_CYAN

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(10.5), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    # Slide number
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
            p.font.color.rgb = TEXT_WHITE if line.startswith("•") or line.startswith("✓") else TEXT_MUTED
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
# SLIDE 1: Title Slide
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

# Badge
badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(3.2), Inches(0.38))
badge.fill.solid()
badge.fill.fore_color.rgb = INDIGO_BADGE
badge.line.fill.background()
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "SUT-ICT-2026-ASEP  |  PHASE 1"
p_b.alignment = PP_ALIGN.CENTER
p_b.font.size = Pt(11)
p_b.font.bold = True
p_b.font.color.rgb = TEXT_WHITE

# Main Title & Subtitle
t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.5), Inches(2.2))
tf = t_box.text_frame
tf.word_wrap = True
p1 = tf.paragraphs[0]
p1.text = "Asepsis: Software-Only Clinical Analytics & Infection Control Platform"
p1.font.size = Pt(32)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE

p2 = tf.add_paragraph()
p2.text = "Deterministic PostgreSQL 16 Backend, Wilson Confidence Intervals & Explainable AI Guardrails"
p2.font.size = Pt(16)
p2.font.color.rgb = PRIMARY_CYAN

# Three Metric Highlights
add_card(s1, Inches(0.8), Inches(3.6), Inches(3.6), Inches(1.7), stat_hero="917", stat_label="Benchmark Dataset (2017)", body="Clinical observation opportunities observed across 5 wards in Debre Berhan Referral Hospital.", highlight=True)
add_card(s1, Inches(4.8), Inches(3.6), Inches(3.6), Inches(1.7), stat_hero="22.0%", stat_label="Baseline Compliance Rate", body="202 compliant actions out of 917 opportunities. 95% Wilson CI: [19.5% – 24.8%].", highlight=True)
add_card(s1, Inches(8.8), Inches(3.6), Inches(3.7), Inches(1.7), stat_hero="30 / 30", stat_label="Pytest Test Suite", body="100% automated test pass rate in 5.06s across schema, queries, ML and safety guardrails.", highlight=True)

# Team Footer
f_box = s1.shapes.add_textbox(Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.4))
tf_f = f_box.text_frame
tf_f.word_wrap = True
p = tf_f.paragraphs[0]
p.text = "Elsewedy University of Technology (SUT)  •  Software Engineering & Data Science / ICT"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = PRIMARY_CYAN

p = tf_f.add_paragraph()
p.text = "Student Team: Zeinab Ismail (Back-End Lead), Amr Khaled (Team Leader & Front-End), Kareem Tamer (Front-End), Jana Osama (QA & Docs), Youmna Mohamed (AI/ML), Omar Nageh (AI/ML), Mohamed Magdy (DBA)"
p.font.size = Pt(10.5)
p.font.color.rgb = TEXT_WHITE

p = tf_f.add_paragraph()
p.text = "Supervisors: Dr. Rehab Farouk (Associate Prof.)  •  Eng. Hend Adel (Teaching Assistant)"
p.font.size = Pt(10.5)
p.font.color.rgb = TEXT_MUTED

# ==============================================================================
# SLIDE 2: Problem Definition & Motivation
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "The Clinical & Technical Challenge", "Why Conventional Healthcare Dashboards Fail", "02 / 12")

add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.3),
         title="⚠️ Manual Spreadsheet Pitfalls",
         body="• Ignores Small Sample Sizes (n): A compliance rate from 2 observations is given the same weight as 200 observations.\n• Premature Department Ranking: Wards are falsely ranked as 'best' or 'worst' based on random sampling noise.\n• CSV Formula Injection Risks: Staff spreadsheets vulnerable to DDE injection attacks (=, +, -, @).\n• Hawthorne Observer Bias Ignored: Fails to document that adherence temporarily spikes when observers are present.")

add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.3),
         title="⚠️ Naive Machine Learning & Leakage Traps",
         body="• Catastrophic Target Leakage: Models trained on variables that deterministically encode the compliance outcome:\n  - HHaction populated exclusively when Complied='Yes'\n  - Missedbutglove populated exclusively when Complied='No'\n• Unchecked Serial Indexing Defects: Gaps and duplicates in hospital observation counters (Opp 788 duplicated, Opp 787 missing).\n• Causality Overclaiming: Interpreting cross-sectional associations as causal without prospective clinical controls.")

add_banner(s2, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.85),
           "🛡️ Asepsis Core Philosophy: Statistical Honesty Over Artificial Hype. Every rate carries a Wilson confidence interval; false rankings are strictly blocked when chi-square p >= 0.05.", "amber")

# ==============================================================================
# SLIDE 3: System Architecture
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "System Engineering & Architecture", "End-to-End Modular Full-Stack Pipeline", "03 / 12")

add_card(s3, Inches(0.8), Inches(1.6), Inches(3.6), Inches(3.8),
         title="1. Relational Database",
         body="• PostgreSQL 16 (production) & SQLite (dev).\n• Normalized 3NF entity schema.\n• Secured pre-aggregated views.\n• Composite primary keys.\n• RBAC JWT auth (admin/analyst/viewer).")

add_card(s3, Inches(4.8), Inches(1.6), Inches(3.6), Inches(3.8),
         title="2. FastAPI Statistical Engine",
         body="• 100% database-backed endpoints.\n• Sub-10ms response latency.\n• Wilson score 95% binomial CIs.\n• Automated Pearson chi-square tests.\n• Privacy rate withholding (n < 5).",
         highlight=True)

add_card(s3, Inches(8.8), Inches(1.6), Inches(3.7), Inches(3.8),
         title="3. UI & Explainable AI",
         body="• Interactive 3-page web dashboard.\n• Chart.js Wilson error whiskers.\n• Logistic Regression vs Baselines.\n• Transparent odds ratios exp(beta).\n• Read-only Clinical Decision Copilot.")

add_banner(s3, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.2),
           "Pipeline Execution Flow:\nRaw Audit CSV ➔ Automated Schema & Leakage Guard ➔ PostgreSQL Relational Tables ➔ Indexed View (v_compliance_facts) ➔ FastAPI Analytics Engine (<10ms) ➔ Interactive Dashboard & Reports", "blue")

# ==============================================================================
# SLIDE 4: PostgreSQL 16 Relational Schema
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Track A & Track B Integration", "PostgreSQL 16 Normalized Database Schema", "04 / 12")

# Create a styled Table
rows, cols = 6, 3
tbl_shape = s4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.2))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.0)
tbl.columns[1].width = Inches(3.8)
tbl.columns[2].width = Inches(4.9)

headers = ["Table Name", "Keys & Integrity Constraints", "Core Function & Clinical Guardrails"]
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
    ("institutions", "id SERIAL PRIMARY KEY, name UNIQUE", "Hospital facility registry ('Debre Berhan referral hospital')."),
    ("wards", "id SERIAL, UNIQUE(institution_id, name)", "Normalized clinical departments (Ob/Gyn, Paediatric, Medical, Surgical, NICU)."),
    ("data_imports", "sha256 UNIQUE, status IN ('committed', 'archived')", "Immutable import ledger preventing re-importing duplicate files; stores audit warnings."),
    ("hand_hygiene_opportunities", "UNIQUE(import_id, row_number), CHECK constraints", "Stores 917 opportunities; preserves Opp 788 duplicate; typed WHO categorical fields."),
    ("model_runs & audit_log", "id SERIAL, JSON fields, indexed timestamps", "Full ML reproducibility lineage and append-only user query audit trail with client IP."),
]

for row_idx, (c0, c1, c2) in enumerate(data, start=1):
    for col_idx, text_val in enumerate([c0, c1, c2]):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = text_val
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_WHITE if col_idx == 0 else TEXT_MUTED

add_banner(s4, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "✓ Schema Conformance: Fully implements schema.sql with zero invented patient/worker IDs, upholding Egyptian Data Protection Law No. 151/2020.", "green")

# ==============================================================================
# SLIDE 5: Secured Database Views & Anti-Leakage
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "Data Governance & Zero Leakage", "Secured Relational Views (v_ml_features & v_compliance_facts)", "05 / 12")

add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.3),
         title="View: v_ml_features",
         body="SQL Definition:\nSELECT w.name AS ward, o.profcat, o.shift, o.indication, o.complied\nFROM hand_hygiene_opportunities o\nJOIN wards w ON w.id = o.ward_id\nJOIN data_imports i ON i.id = o.import_id\nWHERE i.status = 'committed';\n\nKey Guardrails:\n• Exposes strictly permitted predictors.\n• Target-leaking columns (HHaction, Missedbutglove) are physically omitted.\n• Filtered strictly by status = 'committed'.")

add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.3),
         title="View: v_compliance_facts",
         body="SQL Definition:\nSELECT w.name AS ward, o.shift, o.profcat, o.indication,\n       COUNT(*) AS n,\n       SUM(CASE WHEN o.complied THEN 1 ELSE 0 END) AS complied_count\nFROM hand_hygiene_opportunities o\nJOIN wards w ON w.id = o.ward_id\nJOIN data_imports i ON i.id = o.import_id\nWHERE i.status = 'committed'\nGROUP BY w.name, o.shift, o.profcat, o.indication;\n\nKey Performance Benefits:\n• Pre-aggregates fact dimensions into ~60 rows.\n• Enables sub-10ms analytical queries directly in SQL.\n• Completely eliminates raw CSV reading in production.")

add_banner(s5, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.85),
           "🔒 Leakage Isolation: Both views enforce that data analysts and ML pipelines can never query unvalidated or archived imports or leaky variables.", "green")

# ==============================================================================
# SLIDE 6: Data Integrity & Audit Findings
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Data Audit & Integrity Verification", "Anomalies Audited in Debre Berhan Benchmark", "06 / 12")

add_card(s6, Inches(0.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="1. Target Leakage Identified",
         body="Audit Evidence:\n• HHaction is populated in exactly all 202 compliant rows and empty in all 715 non-compliant rows.\n• Missedbutglove is empty in all 202 compliant rows and populated in all 715 non-compliant rows.\n\nResolution:\nBoth columns are isolated from all ML modeling pipelines.")

add_card(s6, Inches(4.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="2. Serial Sequence Defects",
         body="Audit Evidence:\n• Observation ID 788 is duplicated (appears twice).\n• Observation ID 787 is missing entirely.\n\nResolution:\nOpp is treated strictly as an observational serial counter, never a feature. Uniqueness is governed by composite key (import_id, row_number).")

add_card(s6, Inches(8.8), Inches(1.6), Inches(3.7), Inches(4.2),
         title="3. Departmental Confounding",
         body="Audit Evidence:\n• 100% of Midwives in the dataset are assigned to Ob/Gyn ward.\n• Zero Midwives exist in any other clinical ward.\n\nResolution:\nSystem automatically surfaces a confounding disclosure: Ward and Midwife effects cannot be statistically disentangled.")

add_banner(s6, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🛡️ Ingestion Engine: Automated pre-flight CSV validator computes SHA-256 hash, blocks malformed files, and logs 5 diagnostic warnings into data_imports.notes.", "blue")

# ==============================================================================
# SLIDE 7: Statistical Honesty Engine
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Mathematical Rigor & Hypothesis Testing", "Statistical Honesty & Significance Guardrails", "07 / 12")

add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2),
         title="Wilson Score 95% Binomial CIs",
         body="Formula:\np_center = (p + z^2 / 2n) / (1 + z^2 / n)\nmargin = z * sqrt(p(1-p)/n + z^2 / 4n^2) / (1 + z^2 / n)\n\nWhy Wilson CI Matters in Healthcare:\n• Asymmetric bounds that respect the [0, 1] probability boundary.\n• Robust for extreme proportions and small sample sizes where standard Wald intervals fail.\n• Applied to 100% of percentages on dashboard and reports.")

add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2),
         title="Pearson Chi-Square Independence Tests",
         body="Hypothesis Testing Results across Cohort:\n• WHO Indication: chi2 = 369.4, p < 0.001 ➔ Statistically Significant.\n• Wards: chi2 = 5.86, p = 0.21 ➔ Insignificant (p >= 0.05).\n• Shifts: chi2 = 1.05, p = 0.59 ➔ Insignificant (p >= 0.05).\n• Professions: chi2 = 0.63, p = 0.89 ➔ Insignificant (p >= 0.05).\n\nClinical Verdict: Differences between wards, shifts, and roles are indistinguishable from random noise.")

add_banner(s7, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "⚠️ Anti-Ranking Rule: Whenever p >= 0.05, the backend returns: 'No statistically detectable difference between groups; do not rank them.' The UI displays an amber alert box suppressing ranking.", "amber")

# ==============================================================================
# SLIDE 8: Backend Migration & Performance
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Track B Deliverables (Zeinab Ismail)", "Database-Backed FastAPI Service & Performance", "08 / 12")

add_card(s8, Inches(0.8), Inches(1.6), Inches(3.6), Inches(1.8), stat_hero="< 10 ms", stat_label="Query Response Latency", body="Proposal KPI required < 200 ms. Achieved < 10 ms across all dynamic multi-dimensional filters.", highlight=True)
add_card(s8, Inches(4.8), Inches(1.6), Inches(3.6), Inches(1.8), stat_hero="n < 5", stat_label="Privacy Rate Withholding", body="Subgroup rates with n < 5 are masked to prevent individual healthcare worker identification.", highlight=True)
add_card(s8, Inches(8.8), Inches(1.6), Inches(3.7), Inches(1.8), stat_hero="n < 30", stat_label="Small-Sample Warning", body="Subgroups with n < 30 are explicitly flagged with wide confidence interval warnings.", highlight=True)

add_card(s8, Inches(0.8), Inches(3.6), Inches(11.7), Inches(2.2),
         title="Frozen REST API Endpoint Suite Delivered",
         body="• GET /api/v1/analytics/summary — Total opportunities, actions, compliance rate, and Wilson 95% CI.\n• GET /api/v1/analytics/by-{dimension} — Dynamic breakdown (indication, ward, shift, profcat) with chi-square test.\n• GET /api/v1/analytics/records — Searchable, paginated audit records with SQL LIMIT/OFFSET.\n• GET /api/v1/reports/summary — Structured executive audit summary report with clinical limitations.\n• GET /api/v1/reports/export-csv — DDE formula injection-sanitized spreadsheet export.\n• POST /api/v1/auth/login & GET /api/v1/auth/me — Secure JWT token authentication with RBAC.")

add_banner(s8, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "✓ Contract Conformance: 100% of FastAPI analytical endpoints migrated from CSV to indexed SQL queries, meeting all Track B requirements.", "green")

# ==============================================================================
# SLIDE 9: Leakage-Free ML Benchmarks
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
apply_background(s9)
add_header(s9, "Track D: Machine Learning & XAI", "Leakage-Free ML Benchmarking & Model Evaluation", "09 / 12")

rows, cols = 6, 4
tbl_shape = s9.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(3.6))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.2)
tbl.columns[1].width = Inches(3.2)
tbl.columns[2].width = Inches(2.0)
tbl.columns[3].width = Inches(3.3)

headers = ["Model Architecture", "Feature Subset", "ROC-AUC (5-Fold CV)", "Clinical Interpretation"]
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
    ("Dummy Classifier", "Prior prevalence", "0.500", "Baseline random guessing level."),
    ("Indication-Only LogReg", "Indication only", "0.892", "Single clinical rule drives predictive capacity."),
    ("All-Features LogReg", "Ward, Shift, Profcat, Indication", "0.912", "Indication holds 94% of permutation importance."),
    ("Random Forest", "All 4 features", "0.915", "Marginal gain (<0.003) rejected for simplicity."),
    ("Ablation without Indication", "Ward, Shift, Profcat only", "0.528", "Collapses to random chance without Indication."),
]

for row_idx, (c0, c1, c2, c3) in enumerate(data, start=1):
    for col_idx, text_val in enumerate([c0, c1, c2, c3]):
        cell = tbl.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = text_val
        p.font.size = Pt(10)
        p.font.bold = True if col_idx == 2 and "0.9" in text_val else False
        p.font.color.rgb = ACCENT_GREEN if col_idx == 2 and "0.9" in text_val else (TEXT_WHITE if col_idx == 0 else TEXT_MUTED)

add_banner(s9, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.4),
           "🎯 Explainable Odds Ratios: Logistic Regression reveals that compliance 'After body fluid exposure' has an odds ratio OR = 10.8 (p < 0.001) compared to 'Before patient contact'. Healthcare workers instinctively self-protect post-exposure; interventions must focus on pre-contact moments.", "green")

# ==============================================================================
# SLIDE 10: Automated Pytest Verification Suite
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
apply_background(s10)
add_header(s10, "Quality Assurance & Verification", "Automated Pytest Suite: 30 / 30 Passed", "10 / 12")

add_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.3),
         title="Comprehensive Test Categories (30 Tests)",
         body="• Database Schema & Views (8 tests):\n  Column integrity, status filtering, table constraints, latency < 200ms benchmark, reference integrity.\n• Descriptive Analytics (10 tests):\n  Exact 22.0% reproduction, group totals consistency, chi-square p-values, Wilson CI edge cases.\n• Security & Privacy (4 tests):\n  Bcrypt password hashing, formula injection sanitization, n < 5 rate withholding, n < 30 warnings.\n• ML & XAI Engine (3 tests):\n  Automated leakage guard, odds ratios, scenario explainer.\n• Decision Copilot Agent (3 tests):\n  Anti-ranking guardrail, causality refusal, audit rediscovery.")

add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.3),
         title="Automated Test Execution Benchmark",
         body="Test Command:\npython -m pytest backend/tests -v\n\nExecution Environment:\n• Python 3.11.9 on Windows 11\n• SQLAlchemy 2.0 + SQLite/PostgreSQL\n• 30 passed in 5.06 seconds\n• Zero test failures or regressions\n\nKPI Requirement:\nProposal required >= 25 passing tests.\nDelivered: 30 passing tests (+20% margin).",
         highlight=True)

add_banner(s10, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.85),
           "✓ Verification Standard: Rigorous continuous integration guarantees zero breaking changes across all backend API contracts.", "blue")

# ==============================================================================
# SLIDE 11: Front-End Team Handoff & Collaboration
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
apply_background(s11)
add_header(s11, "Team Integration & Collaboration", "Front-End Developer Handoff Kit", "11 / 12")

add_card(s11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.3),
         title="Delivered for Amr Khaled & Kareem Tamer",
         body="• FRONTEND_INTEGRATION_GUIDE.md placed directly in frontend/ directory.\n• Complete endpoint directory with exact query parameters and casing rules.\n• Drop-in Chart.js Error Whisker plugin code to render 95% Wilson confidence intervals.\n• Alert banner code to render amber non-significance alert when p >= 0.05.\n• JavaScript helper snippets for metric cards, data tables, and CSV exports.")

add_card(s11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.3),
         title="Mock Data vs Live API Toggle",
         body="The client module frontend/js/api.js provides seamless dual-mode capability:\n\n• Live Mode: Directly invokes FastAPI database endpoints (<10ms).\n• Mock Mode: Offline fallback to frozen Week 1-2 JSON files.\n• Automatic Failover: Catches network interruptions and falls back to mock files with header notification badge.\n• Zero Build Step: Pure HTML5/ES6 architecture runs directly from any browser.")

add_banner(s11, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.85),
           "🤝 Full Team Alignment: Front-End team has frozen contracts and live endpoints ready for full UI binding.", "green")

# ==============================================================================
# SLIDE 12: Summary & Phase Two Roadmap
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
apply_background(s12)
add_header(s12, "Milestones & Future Outlook", "Phase One Complete — Phase Two Roadmap", "12 / 12")

add_card(s12, Inches(0.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="Track B Accomplishments",
         body="✓ PostgreSQL 16 schema mapped.\n✓ 100% database-backed engine.\n✓ Sub-10ms query latency.\n✓ Wilson CIs & Chi-square guardrails.\n✓ 30 automated pytest tests passing.\n✓ Complete technical documentation.")

add_card(s12, Inches(4.8), Inches(1.6), Inches(3.6), Inches(4.2),
         title="Phase One Status (Week 6)",
         body="• Track A (Data Audit & Schema): Complete.\n• Track B (Backend & Stats API): Complete.\n• Track C (UI Wireframes): In Progress.\n• Track D (ML Benchmarking): Complete.\n• Track E (AI Decision Agent): Complete.\n• Proposal Documentation: Finalized.")

add_card(s12, Inches(8.8), Inches(1.6), Inches(3.7), Inches(4.2),
         title="Phase Two Milestones",
         body="🚀 Live frontend-to-backend binding.\n🏥 Stakeholder interviews (3–5 IPC nurses in Egyptian hospitals).\n📄 GAHAR accreditation audit templates.\n🔒 Deployment on institutional servers.\n🎓 Final thesis defense (Release v1.0).",
         highlight=True)

add_banner(s12, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.85),
           "🎓 Thank you to our supervisors Dr. Rehab Farouk and Eng. Hend Adel for their continuous guidance and feedback.", "blue")

# Save Presentation
output_path = Path("C:/Users/zeina/.gemini/antigravity/scratch/biopress-analytics/Asepsis_Milestone_Defense.pptx")
prs.save(str(output_path))
print(f"[+] Successfully generated PowerPoint presentation: {output_path} ({len(prs.slides)} slides)")

# Also copy to docs/
docs_output = Path("C:/Users/zeina/.gemini/antigravity/scratch/biopress-analytics/docs/Asepsis_Milestone_Defense.pptx")
prs.save(str(docs_output))
print(f"[+] Also saved to: {docs_output}")
