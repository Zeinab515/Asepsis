# BIOPRESS Analytics — UI Wireframes & Layout Specifications (Weeks 1–2)

**Team**: Web Frontend Team  
**Milestone**: Week 1–2 Deliverable (Wireframes, Approved by Database and AI Teams)  
**Target Resolution**: Desktop (1280px+), Tablet (768px–1024px), Mobile (375px–767px)  
**Accessibility**: WCAG 2.1 AAA Compliant (Colorblind-safe, Accessible Contrast, Clear Error Indicators)  

---

## 1. Design Rationale & Ground Rules

In accordance with Section 3.4 of the Cross-Team Engineering Plan:
1. **Uncertainty is First-Class**: Every statistic must be visually paired with numerator, denominator, and Wilson 95% Confidence Interval error whiskers.
2. **Anti-Ranking Layout**: For dimensions where differences are statistically non-significant (Ward $p=0.21$, Shift $p=0.59$, Profession $p=0.89$), groups are displayed neutrally by sample size—NEVER as a competitive leaderboard or color-coded as "best/worst."
3. **Permanent Ethical Disclosure**: Every page anchors a fixed observational disclosure footer emphasizing that data reflects a single hospital in 2017 and must never be used to rank or discipline staff.

---

## 2. Wireframe 1: Desktop Overview Dashboard (Week 5 Focus)

```text
+------------------------------------------------------------------------------------------------------------------------+
|  [BP] BIOPRESS Analytics  |  Debre Berhan Referral Hospital  |  v1.0         [Data Source: Live API | Mock Data]  [Role]  |
+------------------------------------------------------------------------------------------------------------------------+
|  [Tab: Overview (Wk 5)]  |  [Tab: Wireframes (Wk 1-2)]  |  [Tab: API Contract (Wk 1-2)]  |  [Tab: Shared Components]   |
+------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                        |
|  [!] Observational Audit Cohort: Debre Berhan Referral Hospital (Ethiopia, 2017). n=917 opportunities across 5 wards.  |
|                                                                                                                        |
|  +-- SHARED COMPONENT: FILTER BAR -----------------------------------------------------------------------------------+ |
|  | Ward: [ All Wards (5)      v ]  Shift: [ All Shifts (3) v ]  Profession: [ All (4) v ]  Indication: [ All (5) v ]| |
|  |                                                                                [ Apply Filters ] [ Reset ]       | |
|  +-------------------------------------------------------------------------------------------------------------------+ |
|                                                                                                                        |
|  +-- SHARED COMPONENT: STAT CARDS GRID ------------------------------------------------------------------------------+ |
|  | +-----------------------------+  +-----------------------------+  +-----------------------------+                 | |
|  | | OVERALL COMPLIANCE          |  | TOTAL AUDITED OPPORTUNITIES |  | INFECTION CONTROL ACTIONS   |                 | |
|  | | 22.0%                       |  | 917                         |  | 202                         |                 | |
|  | | 202 / 917 actions           |  | Observational audit cohort  |  | Validated hand hygiene wash |                 | |
|  | | [95% CI: 19.5% - 24.8%]     |  | Debre Berhan Referral Hosp. |  | Wilson CI coverage         |                 | |
|  | +-----------------------------+  +-----------------------------+  +-----------------------------+                 | |
|  +-------------------------------------------------------------------------------------------------------------------+ |
|                                                                                                                        |
|  +-- PRIMARY CHART: COMPLIANCE BY WHO INDICATION MOMENT (Chart.js with Wilson CI Error Whiskers) --------------------+ |
|  | Header: Compliance by WHO Moment (Sole Statistically Significant Dimension, p < 0.001)           [Badge: p < 0.001]| |
|  |                                                                                                                   | |
|  |  After body fluid exposure           [=============================================]--|--- 75.8% (113/149)        | |
|  |                                                                                [68.4% - 82.0%]                     | |
|  |  After patient contact               [=========================]------|------- 42.8% (71/166)                     | |
|  |                                                                   [35.5% - 50.4%]                                 | |
|  |  Before an aseptic procedure         [==]--|-- 3.6% (7/195)                                                       | |
|  |                                         [1.7% - 7.2%]                                                             | |
|  |  After patient surroundings          [==]--|-- 3.3% (5/152)                                                       | |
|  |                                         [1.4% - 7.5%]                                                             | |
|  |  Before patient contact              [=]--|-- 2.4% (6/255)                                                        | |
|  |                                         [1.1% - 5.0%]                                                             | |
|  |  +-----------------------------------+-----------------------------------+------------------------------------+    | |
|  |  0%                                  25%                                 50%                                 100% | |
|  +-------------------------------------------------------------------------------------------------------------------+ |
|                                                                                                                        |
|  +-- DATA-SOURCE CONTEXT CARD ---------------------------------------------------------------------------------------+ |
|  | Study: Kolola & Gezahegn (2017) &bull; Cross-sectional observation across Medical, NICU, Ob/Gyn, Paediatric,      | |
|  | and Surgical wards. Hawthorne effect likely elevated compliance. Hand washing was highest after bodily exposure. | |
|  +-------------------------------------------------------------------------------------------------------------------+ |
|                                                                                                                        |
+------------------------------------------------------------------------------------------------------------------------+
|  PERMANENT FOOTER: Observational audit data (Debre Berhan, 2017). Hawthorne effect possible. Not live monitoring.      |
|  Strict non-disciplinary policy: Metrics describe systemic moments and MUST NEVER be used to rank individual staff.   |
+------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Wireframe 2: Shared Component Anatomy (Week 5 Focus)

### Component A: Stat Card (`stat-card`)
```text
+-------------------------------------------------------+
|  LABEL (Uppercase, 11px Bold)                  [ICON] |
|  32px Numeric Value (e.g. 22.0% or 917)               |
|  Subtitle: Numerator / Denominator (202 / 917)        |
|  [ Badge: 95% Wilson CI [19.5% - 24.8%] ]             |
+-------------------------------------------------------+
```

### Component B: Filter Bar (`filter-bar`)
```text
+----------------------------------------------------------------------------------------+
| [Ward Select v]  [Shift Select v]  [Profession Select v]  [Indication v]  [Apply] [Reset] |
+----------------------------------------------------------------------------------------+
```

### Component C: Honesty & Warning Banners (`banner`)
```text
[Neutral / Info Notice]
+----------------------------------------------------------------------------------------+
| (i) Notice: Chi-square test (p = 0.21 > 0.05). No statistically detectable difference   |
|     between hospital wards. Do not treat observed differences as rankings.             |
+----------------------------------------------------------------------------------------+

[Small-Sample Warning]
+----------------------------------------------------------------------------------------+
| /!\ Warning: Subgroup sample size is below 30 (n = 12). Wilson interval is wide.       |
+----------------------------------------------------------------------------------------+
```

### Component D: Accessible Data Table (`data-table`)
```text
+----------------------------------------------------------------------------------------+
| Dimension Category | Compliance Rate (%) | Count (k / n) | Wilson 95% CI | Sample Eval |
+--------------------+---------------------+---------------+---------------+-------------+
| Nurse              | [===] 22.9%         | 109 / 476     | [19.3%-26.9%] | [Adequate]  |
| Medical doctor     | [===] 20.6%         | 51 / 248      | [15.9%-26.1%] | [Adequate]  |
| Midwife            | [===] 21.2%         | 29 / 137      | [15.1%-28.8%] | [Adequate]  |
| Other              | [===] 23.2%         | 13 / 56       | [14.0%-35.8%] | [Adequate]  |
+----------------------------------------------------------------------------------------+
```

---

## 4. Wireframe 3: Mobile Breakpoint Layout (< 768px)

On mobile viewports:
- Header collapses into brand logo, hospital badge, and data source toggle.
- Filter bar stacks vertically into full-width dropdown controls.
- Stat cards collapse from a 3-column row into a single-column stack.
- Chart displays horizontally with enlarged touch tooltips.
- The footer remains anchored with legible, accessible contrast.
