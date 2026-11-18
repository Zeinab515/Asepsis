import pytest
import pandas as pd
from app.ml import evaluate
from app.services.data_loader import get_frame


def test_leakage_guard_raises_error_if_leaky_columns_provided():
    raw_df = get_frame()
    # Attempting to load ML dataset with HHaction or Missedbutglove should fail immediately
    with pytest.raises(ValueError) as exc:
        evaluate.load_ml_dataset(raw_df[["Ward", "Profcat", "Shift", "Indication", "HHaction", "complied"]])
    assert "Target leakage column" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        evaluate.load_ml_dataset(raw_df[["Ward", "Profcat", "Shift", "Indication", "Missedbutglove", "complied"]])
    assert "Target leakage column" in str(exc.value)


def test_odds_ratios_computation_and_references():
    df = evaluate.load_ml_dataset()
    ors = evaluate.compute_odds_ratios(df)

    assert len(ors) > 0
    # Check reference category for Indication
    ind_ors = [x for x in ors if x["feature"] == "Indication"]
    assert len(ind_ors) == 4  # 5 indications minus reference
    for x in ind_ors:
        assert x["reference_category"] == "Before patient contact"

    # After body fluid exposure must have huge odds ratio and p < 0.001
    bf_exp = next(x for x in ind_ors if "body fluid" in x["category"].lower())
    assert bf_exp["odds_ratio"] > 10.0
    assert bf_exp["p_value"] < 0.001
    assert bf_exp["is_significant"] is True

    # Check Ob/Gyn and Midwife confounding warning
    ob_gyn = next(x for x in ors if x["feature"] == "Ward" and x["category"] == "Ob/Gyn")
    assert ob_gyn["confounding_warning"] is not None

    midwife = next(x for x in ors if x["feature"] == "Profcat" and x["category"] == "Midwife")
    assert midwife["confounding_warning"] is not None


def test_local_opportunity_explanation():
    res = evaluate.explain_single_opportunity(
        ward="Medical",
        profcat="Nurse",
        shift="Morning",
        indication="After body fluid exposure",
    )
    assert "predicted_probability" in res
    assert 0.0 <= res["predicted_probability"] <= 1.0
    assert res["subgroup_sample_size"] > 0
    assert "ethics_disclaimer" in res
