import pytest
from app.core.security import create_access_token, get_password_hash, sanitize_csv_cell, verify_password
from app.services import analytics
import pandas as pd


def test_password_hashing_and_verification():
    pwd = "SecureSecretPassword2026!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_csv_formula_injection_sanitization():
    # Dangerous spreadsheet formulas
    assert sanitize_csv_cell("=CMD|' /C calc'!A0") == "'=CMD|' /C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-12345") == "'-12345"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    # Safe values untouched
    assert sanitize_csv_cell("Medical") == "Medical"
    assert sanitize_csv_cell("202") == "202"
    assert sanitize_csv_cell(None) == ""


def test_privacy_withholding_when_n_below_5():
    # Build tiny cohort of n=3
    df = pd.DataFrame({
        "Ward": ["Medical", "Medical", "Medical"],
        "complied": [1, 0, 1],
    })
    res = analytics.by_group(df, "ward")
    row = res["rows"][0]
    assert row["n"] == 3
    assert row["is_withheld"] is True
    assert row["rate"] is None, "Rate must be withheld when n < 5 for privacy protection!"


def test_small_sample_warning_when_n_below_30():
    # Cohort of n=10 (between 5 and 30)
    df = pd.DataFrame({
        "Ward": ["Medical"] * 10,
        "complied": [1] * 5 + [0] * 5,
    })
    res = analytics.by_group(df, "ward")
    row = res["rows"][0]
    assert row["n"] == 10
    assert row["is_withheld"] is False
    assert row["is_small_sample"] is True
    assert row["rate"] == 0.5
