# Model Card — BIOPRESS Analytics Hand Hygiene Compliance Models

Following the framework of Mitchell et al. (2019) *Model Cards for Model Reporting*.

---

## 1. Model Details

- **Model Name**: BIOPRESS Compliance Classifier (Phase 1 Baseline & Benchmarks)
- **Primary Architecture**: Logistic Regression with $L_2$ Regularization (`C=1.0`) inside a Scikit-Learn `Pipeline` with `OneHotEncoder(handle_unknown='ignore')`.
- **Benchmark Comparators**:
  1. `DummyClassifier(strategy='prior')`: baseline chance model.
  2. `DecisionTreeClassifier(max_depth=3)`: rule-based interpretable tree.
  3. `RandomForestClassifier(n_estimators=100, max_depth=5)`: non-linear comparison.
- **Framework**: Scikit-Learn 1.4+, SciPy 1.11+, Python 3.11.
- **Evaluation Artifact**: `data/reports/ml_evaluation_report.json`.

---

## 2. Intended Use

- **Intended Task**: Descriptive auditing and clinical opportunity risk profiling to identify WHO hand hygiene contact moments associated with high non-compliance.
- **Intended Users**: Hospital Infection Prevention and Control (IPC) committees, clinical quality officers, and public health researchers.
- **Application Context**: Debre Berhan Referral Hospital, Ethiopia.

### Out-of-Scope Uses
> [!CAUTION]
> **Strict Ethical Prohibition**:
> - **Staff Performance Ranking**: The model MUST NEVER be used to evaluate, grade, rank, or discipline individual doctors, nurses, or midwives.
> - **Causal Attribution**: The model estimates observational correlations. It cannot determine the psychological, physical, or environmental causes of missed compliance.
> - **Cross-Hospital Deployment**: Findings reflect a single hospital's physical layout and workflow in 2017; predictions cannot be transferred to other facilities without local retraining.

---

## 3. Data Lineage & Target Leakage Guard

- **Audit Source**: Published study by Kolola & Gezahegn (2017), Debre Berhan Referral Hospital.
- **Cohort Size**: 917 observed opportunities, 202 compliant actions (22.0% compliance rate).

### Target Leakage Exclusions
| Excluded Column | Leakage Finding | Action |
|---|---|---|
| `HHaction` | Populated in 100% of compliant rows (`Complied=Yes`); empty in 100% of non-compliant rows | **Strictly barred** from feature sets |
| `Missedbutglove` | Populated in 100% of non-compliant rows (`Complied=No`); empty in 100% of compliant rows | **Strictly barred** from feature sets |
| `Opp` | Observation sequence ID with duplicate (788) and missing (787) numbers | **Excluded** from features |

### Allowed Features
`Ward` (5 categories), `Profcat` (4 categories), `Shift` (3 categories), and `Indication` (5 WHO moments).

---

## 4. Quantitative Performance & Validation Benchmarks

Models were evaluated across three distinct validation designs to test generalization and temporal stability:

### 4.1 Repeated Stratified 5-Fold Cross Validation (50 Runs)
| Model | Ablation Features | ROC-AUC (Mean ± SD) | PR-AUC (Baseline: 0.22) | F1 Score | Brier Score |
|---|---|---|---|---|---|
| **Dummy (Prior)** | All Features | 0.500 ± 0.000 | 0.220 ± 0.002 | 0.000 | 0.172 |
| **Logistic Regression** | Indication Only | 0.886 ± 0.021 | 0.738 ± 0.048 | 0.697 | 0.098 |
| **Logistic Regression** | All 4 Features | **0.907 ± 0.018** | **0.781 ± 0.042** | **0.725** | **0.091** |
| **Decision Tree (d=3)** | All 4 Features | 0.882 ± 0.024 | 0.742 ± 0.051 | 0.695 | 0.101 |
| **Random Forest** | All 4 Features | 0.923 ± 0.016 | 0.804 ± 0.039 | 0.732 | 0.086 |
| **Logistic Regression** | Without Indication | 0.504 ± 0.038 | 0.224 ± 0.021 | 0.000 | 0.171 |

### 4.2 Key Empirical Takeaway & Decision Rule
1. **Indication Dominates Signal**: Removing `Indication` collapses model performance to 0.504 ROC-AUC (equivalent to random guessing).
2. **Simpler Model Preferred**: The difference between Random Forest (0.923) and Logistic Regression (0.907) is within fold-to-fold error margins ($\pm 0.018$). In adherence to clinical governance and interpretability guidelines, **Logistic Regression is the recommended model**.

---

## 5. Explainability (XAI) & Odds Ratios

Logistic Regression coefficients $\beta_j$ converted to Odds Ratios $\exp(\beta_j)$ with 95% Wald confidence intervals:

| Feature | Category | Reference Level | Odds Ratio | 95% Wald CI | p-value | Significance |
|---|---|---|---|---|---|---|
| **Indication** | After body fluid exposure | Before patient contact | **81.67** | [39.35 – 169.51] | &lt; 0.001 | Significant |
| **Indication** | After patient contact | Before patient contact | **14.19** | [7.29 – 27.63] | &lt; 0.001 | Significant |
| **Indication** | After surroundings | Before patient contact | 0.76 | [0.27 – 2.18] | 0.613 | Not Significant |
| **Indication** | Before aseptic procedure | Before patient contact | 0.81 | [0.31 – 2.09] | 0.664 | Not Significant |
| **Ward** | NICU | Medical | 2.36 | [1.11 – 5.03] | 0.026 | Overlaps |
| **Ward** | Paediatric | Medical | 2.18 | [1.18 – 4.02] | 0.013 | Overlaps |
| **Ward** | Ob/Gyn | Medical | 0.54 | [0.24 – 1.18] | 0.122 | Confounded |
| **Ward** | Surgical | Medical | 0.75 | [0.38 – 1.47] | 0.399 | Not Significant |
| **Profcat** | Midwife | Nurse | 1.19 | [0.45 – 3.12] | 0.732 | Confounded |
| **Profcat** | Medical doctor | Nurse | 0.89 | [0.54 – 1.45] | 0.627 | Not Significant |
| **Shift** | Night | Morning | 0.80 | [0.47 – 1.35] | 0.398 | Not Significant |
| **Shift** | After noon | Morning | 0.67 | [0.41 – 1.10] | 0.115 | Not Significant |

---

## 6. Structural Confounding & Clinical Limitations

1. **Midwife / Ob-Gyn Confounding**: All Midwives in the dataset observed only in the Ob/Gyn ward. Their individual contributions cannot be mathematically separated.
2. **Hawthorne Effect**: Direct observational auditing notoriously induces observer-bias, raising compliance rates during the observation window above natural levels.
3. **Clustering & Optimistic Variance**: Absence of unique Healthcare Worker (HCW) identifiers or session numbers prevents multi-level hierarchical modeling; variance estimates may be slightly optimistic due to repeated observations of the same clinician.
