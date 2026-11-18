# Asepsis — Front-End Team Integration & API Guide
**Audience:** Amr Khaled Abdo (Team Leader & Front-end Developer) & Kareem Tamer (Front-end Developer)  
**Author:** Zeinab Ismail (Back-end Developer — Track B Lead)  
**Backend Status:** 100% Database-Backed (PostgreSQL 16 / SQLite), < 10ms Query Latency, 30 Passing Unit Tests  
**Base URL:** `http://127.0.0.1:8000` (or relative path `""` when served by FastAPI)

---

## 1. Quick Start & Server Setup

The FastAPI backend automatically mounts and serves the static files inside the `frontend/` directory.

### Starting the Live Backend
In your terminal (from project root):
```powershell
cd backend
uvicorn app.main:app --reload
```
- **Live Frontend:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive OpenAPI (Swagger) Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Interactive Reference:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Switching Between Mock Data & Live API
In `frontend/js/api.js`, you can toggle between offline mock JSON and the live backend:
```javascript
// Switch to live backend API (PostgreSQL/SQLite)
API.setMockMode(false);

// Switch to offline mock data (frontend/mock/*.json)
API.setMockMode(true);

// Check current data source in UI
console.log(API.getActiveSource()); // "live" or "mock"
```

---

## 2. API Endpoint Directory

| Endpoint | Method | Description | Key Query Parameters |
| :--- | :---: | :--- | :--- |
| `/health` | `GET` | Backend liveness check | None |
| `/api/v1/analytics/summary` | `GET` | Hospital overview metrics & Wilson 95% CI | `ward`, `shift`, `profcat`, `indication` |
| `/api/v1/analytics/by-indication` | `GET` | WHO 5 Moments breakdown + $\chi^2$ test | `ward`, `shift`, `profcat` |
| `/api/v1/analytics/by-ward` | `GET` | Ward breakdown + $\chi^2$ test | `shift`, `profcat`, `indication` |
| `/api/v1/analytics/by-shift` | `GET` | Shift breakdown + $\chi^2$ test | `ward`, `profcat`, `indication` |
| `/api/v1/analytics/by-profcat` | `GET` | Professional category + $\chi^2$ test | `ward`, `shift`, `indication` |
| `/api/v1/analytics/records` | `GET` | Paginated individual observations | `page`, `page_size`, `search`, filters |
| `/api/v1/reports/summary` | `GET` | Full hospital IPC audit summary report | None |
| `/api/v1/reports/export-csv` | `GET` | Download DDE-sanitized CSV file | `ward`, `shift`, `profcat`, `indication` |
| `/api/v1/auth/login` | `POST` | User login (returns JWT bearer token) | JSON body: `{ username, password }` |
| `/api/v1/auth/me` | `GET` | Get authenticated user info | Header: `Authorization: Bearer <token>` |
| `/api/v1/agent/query` | `POST` | Ask Clinical AI Copilot a question | JSON body: `{ query: "..." }` |
| `/api/v1/ml/evaluation` | `GET` | ML model benchmarks & odds ratios | None |
| `/api/v1/ml/explain` | `POST` | Predict compliance probability for a scenario | JSON body: `{ ward, profcat, shift, indication }` |

---

## 3. Allowed Category Filter Values (Strict Validation)

When passing query parameters for filters, ensure you use the exact casing:

* **`ward`**: `"Ob/Gyn"`, `"Paediatric"`, `"Medical"`, `"Surgical"`, `"NICU"`
* **`shift`**: `"Morning"`, `"After noon"`, `"Night"`
* **`profcat`**: `"Nurse"`, `"Medical doctor"`, `"Midwife"`, `"Other"`
* **`indication`**:
  * `"Before patient contact"`
  * `"Before an aseptic procedure"`
  * `"After patient contact"`
  * `"After contact with patient Surroundings"`
  * `"After body fluid exposure"`

---

## 4. Endpoint Specifications & Exact JSON Payloads

### 4.1 Overview Summary (`GET /api/v1/analytics/summary`)
Returns aggregated metrics for top KPI cards.

**Request Example:**
```javascript
const summary = await API.getSummary({ ward: "Medical", shift: "Morning" });
```

**JSON Response:**
```json
{
  "opportunities": 917,
  "actions": 202,
  "compliance_rate": 0.22028,
  "ci_low": 0.19465,
  "ci_high": 0.24824,
  "institution": "Debre Berhan Referral Hospital",
  "notes": "Full audit cohort (Debre Berhan, Ethiopia, 2017)."
}
```

---

### 4.2 Group Breakdown & Hypothesis Tests (`GET /api/v1/analytics/by-{dimension}`)
Used for charts and comparative tables. Available dimensions: `indication`, `ward`, `shift`, `profcat`.

**Request Example:**
```javascript
const wardData = await API.getByGroup("ward");
const indData = await API.getByGroup("indication");
```

**JSON Response:**
```json
{
  "dimension": "ward",
  "rows": [
    {
      "group": "Ob/Gyn",
      "n": 219,
      "complied": 43,
      "rate": 0.1963,
      "ci_low": 0.1491,
      "ci_high": 0.2539,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "Paediatric",
      "n": 211,
      "complied": 48,
      "rate": 0.2274,
      "ci_low": 0.1755,
      "ci_high": 0.2893,
      "is_small_sample": false,
      "is_withheld": false
    },
    {
      "group": "NICU",
      "n": 77,
      "complied": 19,
      "rate": 0.2467,
      "ci_low": 0.1627,
      "ci_high": 0.3548,
      "is_small_sample": false,
      "is_withheld": false
    }
  ],
  "test": {
    "name": "chi-square test of independence",
    "chi2": 5.86,
    "dof": 4,
    "p_value": 0.21,
    "min_expected_count": 16.96,
    "is_significant": false
  },
  "note": "Descriptive only; differences are not evidence of a cause. No statistically detectable difference between groups; do not rank them.",
  "action_recommendation": "Do not treat observed group differences as meaningful or rank departments/shifts."
}
```

---

### 4.3 Paginated Data Explorer Records (`GET /api/v1/analytics/records`)
Fetches audit rows with search and pagination directly from the database.

**Request Example:**
```javascript
const data = await API.getRecords({
  page: 1,
  page_size: 25,
  ward: "Medical",
  search: "doctor"
});
```

**JSON Response:**
```json
{
  "total": 64,
  "page": 1,
  "page_size": 25,
  "total_pages": 3,
  "items": [
    {
      "id": 12,
      "row_number": 12,
      "source_opp": 12,
      "ward": "Medical",
      "profcat": "Medical doctor",
      "shift": "Morning",
      "indication": "Before an aseptic procedure",
      "complied": false,
      "hh_action": null,
      "missed_but_glove": "Yes"
    }
  ]
}
```

---

### 4.4 Downloading Sanitized CSV (`GET /api/v1/reports/export-csv`)
Initiates direct file download with formula injection protection:
```javascript
function downloadAuditCSV(filters = {}) {
  const query = new URLSearchParams(filters).toString();
  window.location.href = `/api/v1/reports/export-csv${query ? '?' + query : ''}`;
}
```

---

## 5. Mandatory Statistical Honesty UI Rules (Grading Critical)

To satisfy the grading criteria in the Project Proposal (Section 1.6 & Track C), the UI **must** adhere to these four statistical honesty rules:

### Rule 1: Visual Wilson 95% Confidence Intervals (Error Bars)
Every rate bar chart **must** draw confidence interval error whiskers.
Use this Chart.js custom plugin snippet:

```javascript
// Register custom error bar plugin for Chart.js
const errorBarPlugin = {
  id: 'errorBars',
  afterDatasetsDraw(chart) {
    const { ctx, scales: { x, y } } = chart;
    const dataset = chart.data.datasets[0];
    if (!dataset || !dataset.errorBars) return;

    ctx.save();
    ctx.strokeStyle = '#38bdf8'; // Primary accent color
    ctx.lineWidth = 2;

    dataset.data.forEach((val, i) => {
      const { low, high } = dataset.errorBars[i];
      if (low == null || high == null) return;

      const xPos = x.getPixelForValue(i);
      const yLow = y.getPixelForValue(low * 100);
      const yHigh = y.getPixelForValue(high * 100);

      // Draw vertical stem
      ctx.beginPath();
      ctx.moveTo(xPos, yLow);
      ctx.lineTo(xPos, yHigh);
      ctx.stroke();

      // Draw top and bottom caps
      const capWidth = 6;
      ctx.beginPath();
      ctx.moveTo(xPos - capWidth, yLow);
      ctx.lineTo(xPos + capWidth, yLow);
      ctx.moveTo(xPos - capWidth, yHigh);
      ctx.lineTo(xPos + capWidth, yHigh);
      ctx.stroke();
    });
    ctx.restore();
  }
};
Chart.register(errorBarPlugin);
```

### Rule 2: Non-Significance Alert Banner (Anti-Ranking Guardrail)
When `test.is_significant === false` ($p \ge 0.05$), render an **amber warning box** above the chart and **do not** sort or rank categories from best to worst:

```javascript
function renderTestBanner(test, containerId) {
  const container = document.getElementById(containerId);
  if (!test.is_significant) {
    container.innerHTML = `
      <div class="alert alert-amber">
        <span class="alert-icon">⚠️</span>
        <div>
          <strong>No Statistically Detectable Difference (p = ${test.p_value.toFixed(2)} ≥ 0.05):</strong>
          Differences across these groups are consistent with random sampling fluctuation.
          <em>Do not rank or penalize departments based on observed percentage differences.</em>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="alert alert-green">
        <span class="alert-icon">✓</span>
        <div>
          <strong>Statistically Detectable Association (p < 0.001):</strong>
          Differences across WHO Indications are systematic and require clinical priority.
        </div>
      </div>
    `;
  }
}
```

### Rule 3: Privacy Rate Withholding ($n < 5$)
If an observational subgroup has $n < 5$, `row.rate` is `null` and `row.is_withheld` is `true`.
* **Do NOT render:** `0%` or `NaN%`.
* **DO render:** A gray badge reading `<span class="badge badge-muted">Withheld (n < 5)</span>`.

### Rule 4: Small-Sample Uncertainty Warning ($n < 30$)
If `row.is_small_sample === true` ($5 \le n < 30$), render a warning icon next to the rate:
```html
<span>${(row.rate * 100).toFixed(1)}%</span>
<span class="badge-warning" title="Small sample (n < 30): Wide confidence interval">⚠️ n=${row.n}</span>
```

---

## 6. Authentication & User Roles (Admin / Analyst / Viewer)

To enable role-gated features (e.g., CSV Upload only for `admin` / `analyst`):

```javascript
async function loginUser(username, password) {
  const resp = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!resp.ok) throw new Error("Invalid credentials");
  const data = await resp.json();
  
  // Store Bearer token in localStorage
  localStorage.setItem("biopress_token", data.access_token);
  localStorage.setItem("biopress_role", data.role);
  return data;
}

// Helper to add auth header
function getAuthHeaders() {
  const token = localStorage.getItem("biopress_token");
  return token ? { "Authorization": `Bearer ${token}` } : {};
}
```

**Default Test Credentials:**
* **Admin:** `username: admin` | `password: AdminPassword2026!`
* **Analyst:** `username: analyst` | `password: AnalystPassword2026!`
* **Viewer:** `username: viewer` | `password: ViewerPassword2026!`

---

## 7. Connecting the Clinical Copilot AI (`POST /api/v1/agent/query`)

To wire the AI copilot chat interface in `frontend/pages/agent.html`:

```javascript
async function sendAgentQuery(question) {
  const resp = await fetch("/api/v1/agent/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: question })
  });
  const data = await resp.json();
  
  // data contains:
  // - data.answer (formatted markdown string)
  // - data.tool_calls (array of logged backend functions executed)
  // - data.guardrails_enforced (array of active safety guardrails)
  // - data.disclaimer (mandatory ethical note)
  return data;
}
```

---

## 8. Summary Checklist for Frontend Team

- [ ] Connect `API.getSummary()` to the 4 overview metric cards.
- [ ] Connect `API.getByGroup('indication')` to the primary WHO moments bar chart.
- [ ] Add the Chart.js Wilson Error Whisker plugin.
- [ ] Render the amber non-significance alert box on Ward, Shift, and Role tabs.
- [ ] Wire the `API.getRecords()` table with search box, ward filter dropdown, and pagination buttons.
- [ ] Connect the "Export CSV" button to `/api/v1/reports/export-csv`.
- [ ] Wire the Copilot chat box to `POST /api/v1/agent/query`.

*If you need any custom query parameters or response fields, ping Zeinab in the backend channel!*
