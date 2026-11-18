from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MetricScore(BaseModel):
    mean: float
    std: float
    ci_low: float
    ci_high: float


class ConfusionMatrixOut(BaseModel):
    tn: int
    fp: int
    fn: int
    tp: int
    total: int


class ModelBenchmarkRow(BaseModel):
    model_name: str
    validation_design: str  # 'repeated_stratified_cv', 'order_opp_split', 'leave_one_ward_out'
    ablation: str  # 'all_features', 'indication_only', 'without_indication'
    pr_auc: MetricScore
    roc_auc: MetricScore
    f1: MetricScore
    precision: MetricScore
    recall: MetricScore
    brier_score: MetricScore
    confusion_matrix: ConfusionMatrixOut
    notes: Optional[str] = None


class OddsRatioRow(BaseModel):
    feature: str
    category: str
    reference_category: str
    odds_ratio: float
    ci_low: float
    ci_high: float
    p_value: float
    is_significant: bool
    interpretation: str
    confounding_warning: Optional[str] = None


class PermutationImportanceRow(BaseModel):
    feature: str
    importance_mean: float
    importance_std: float


class EvaluationReportResponse(BaseModel):
    generated_at: str
    git_commit: str
    dataset_hash: str
    total_opportunities: int
    total_complied: int
    baseline_compliance_rate: float
    benchmark_table: List[ModelBenchmarkRow]
    odds_ratios: List[OddsRatioRow]
    permutation_importance: List[PermutationImportanceRow]
    conclusion: str
    fairness_and_ethics: str


class PredictRequest(BaseModel):
    ward: str
    profcat: str
    shift: str
    indication: str


class PredictResponse(BaseModel):
    predicted_probability: float
    predicted_class: int
    threshold_used: float
    subgroup_observed_rate: Optional[float]
    subgroup_sample_size: int
    model_type: str
    explanation: str
    ethics_disclaimer: str
