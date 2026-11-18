# BIOPRESS Analytics — Frozen Endpoint Contract (Week 2 Milestone)

**Document Type**: Cross-Team Service Level Agreement (SLA) & API Contract  
**Stakeholder Teams**: Web Frontend Team, Database & Security Team, AI/ML Team  
**Contract Status**: **FROZEN (End of Week 2)**  
**Version**: 1.0.0 (OpenAPI 3.0 Specification)  

---

## 1. Ground Rules Agreed by All Teams

1. **Target Leakage Prohibition**:
   `HHaction` is populated in 100% of compliant rows and empty in all non-compliant rows; `Missedbutglove` is populated in 100% of non-compliant rows and empty in all compliant rows. Both leak the target. They are **never** included in API feature models or exposed to the ML team.
2. **Observation Sequence (`Opp`)**:
   Observation ID `788` appears twice, and `787` is missing. It is not an ML feature. The database uses a composite key of `(import_id, row_number)` for uniqueness.
3. **Statistical Honesty**:
   - Every rate returned by the API carries:
     - Numerator ($k$ actions)
     - Denominator ($n$ opportunities)
     - Wilson score 95% Confidence Interval (`ci_low`, `ci_high`)
   - For `Ward` ($p = 0.21$), `Shift` ($p = 0.59$), and `Profcat` ($p = 0.89$), the API explicitly returns:
     `"note": "Descriptive only; differences are not evidence of a cause. No statistically detectable difference between groups; do not rank them."`
   - Privacy: Rates with $n < 5$ are returned as `null` (`is_withheld: true`); groups with $n < 30$ are flagged with `is_small_sample: true`.
4. **Mock Data Guarantee**:
   Until the Database team delivers the PostgreSQL/SQLite integration in Week 4, the Web team builds exclusively against static JSON files in `frontend/mock/` that match these exact JSON schemas.

---

## 2. Frozen Endpoint Specifications

### 2.1 Liveness Probe
- **Endpoint**: `GET /health`
- **Response**: `200 OK`
```json
{
  "status": "ok"
}
```

---

### 2.2 Hospital Summary Endpoint
- **Endpoint**: `GET /api/v1/analytics/summary`
- **Query Parameters (Optional Filters)**:
  - `ward` (string): e.g. `"Medical"`, `"NICU"`, `"Ob/Gyn"`, `"Paediatric"`, `"Surgical"`
  - `shift` (string): `"Morning"`, `"After noon"`, `"Night"`
  - `profcat` (string): `"Nurse"`, `"Medical doctor"`, `"Midwife"`, `"Other"`
  - `indication` (string): One of the WHO 5 Moments
- **Response Model**: `Summary`
```json
{
  "opportunities": 917,
  "actions": 202,
  "compliance_rate": 0.22028,
  "ci_low": 0.19456,
  "ci_high": 0.24838,
  "institution": "Debre Berhan Referral Hospital",
  "notes": "Full audit cohort (Debre Berhan, Ethiopia, 2017)."
}
```

---

### 2.3 Group Breakdown & Hypothesis Testing Endpoints
- **Endpoints**:
  - `GET /api/v1/analytics/by-indication`
  - `GET /api/v1/analytics/by-ward`
  - `GET /api/v1/analytics/by-shift`
  - `GET /api/v1/analytics/by-profcat`
- **Response Model**: `GroupAnalysis`
```json
{
  "dimension": "indication",
  "rows": [
    {
      "group": "After body fluid exposure",
      "n": 149,
      "complied": 113,
      "rate": 0.75838,
      "ci_low": 0.68367,
      "ci_high": 0.81977,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "After patient contact",
      "n": 166,
      "complied": 71,
      "rate": 0.42771,
      "ci_low": 0.35470,
      "ci_high": 0.50406,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "Before an aseptic procedure",
      "n": 195,
      "complied": 7,
      "rate": 0.03589,
      "ci_low": 0.01747,
      "ci_high": 0.07222,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "After contact with patient Surroundings",
      "n": 152,
      "complied": 5,
      "rate": 0.03289,
      "ci_low": 0.01414,
      "ci_high": 0.07466,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "Before patient contact",
      "n": 255,
      "complied": 6,
      "rate": 0.02352,
      "ci_low": 0.01083,
      "ci_high": 0.05035,
      "is_small_sample": false,
      "is_withheld": false
    }
  ],
  "test": {
    "name": "chi-square test of independence",
    "chi2": 419.9234,
    "dof": 4,
    "p_value": 0.0000000000000001,
    "min_expected_count": 32.81,
    "is_significant": true
  },
  "note": "Descriptive only; differences are not evidence of a cause. Overall difference between groups is statistically detectable.",
  "action_recommendation": "Prioritize workflow support for indications where compliance is systematically lower."
}
```

---

### 2.4 Paginated Opportunity Records Endpoint
- **Endpoint**: `GET /api/v1/analytics/records`
- **Query Parameters**: `page` (default 1), `page_size` (default 25), `ward`, `shift`, `profcat`, `indication`, `search`
- **Response Model**: `PaginatedRecords`
```json
{
  "total": 917,
  "page": 1,
  "page_size": 10,
  "total_pages": 92,
  "items": [
    {
      "id": 1,
      "row_number": 1,
      "source_opp": 1,
      "ward": "Medical",
      "profcat": "Nurse",
      "shift": "Morning",
      "indication": "Before patient contact",
      "complied": false,
      "hh_action": null,
      "missed_but_glove": "No"
    }
  ]
}
```

---

## 3. Team Sign-Offs (Week 2 Freeze)
- **Database & Security Team**: Approved schema contracts and composite key uniqueness design.
- **AI/ML Team**: Approved `v_ml_features` exclusion of `hh_action` and `missed_but_glove`.
- **Web Frontend Team**: Approved JSON schemas and validated against `frontend/mock/*.json` files.
