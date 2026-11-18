import io
import time
import pytest
import pandas as pd
from sqlalchemy import inspect, text
from app.db.models import HandHygieneOpportunity, Institution, Ward, DataImport
from app.db.session import SessionLocal, init_db_and_views, engine
from app.services.importer import preview_csv_import, commit_csv_import, validate_csv_structure
from app.services import analytics


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db_and_views(engine)
    yield


def test_views_exist_and_exclude_leakage():
    insp = inspect(engine)
    cols = insp.get_columns("v_ml_features")
    col_names = [c["name"].lower() for c in cols]
    assert "ward" in col_names
    assert "profcat" in col_names
    assert "shift" in col_names
    assert "indication" in col_names
    assert "complied" in col_names
    assert "hh_action" not in col_names and "hhaction" not in col_names, "Target leakage column found in v_ml_features!"
    assert "missed_but_glove" not in col_names and "missedbutglove" not in col_names, "Target leakage column found in v_ml_features!"


def test_compliance_facts_view_structure():
    insp = inspect(engine)
    cols = insp.get_columns("v_compliance_facts")
    col_names = [c["name"].lower() for c in cols]
    assert "ward" in col_names
    assert "shift" in col_names
    assert "profcat" in col_names
    assert "indication" in col_names
    assert "n" in col_names
    assert "complied_count" in col_names


def test_views_respect_committed_status_filter():
    db = SessionLocal()
    try:
        # Check that compliance facts aggregate matches hand_hygiene_opportunities with status='committed'
        res = db.execute(text("SELECT SUM(n), SUM(complied_count) FROM v_compliance_facts;")).fetchone()
        assert int(res[0]) == 917
        assert int(res[1]) == 202
    finally:
        db.close()


def test_import_detects_contract_warnings_and_leakage():
    csv_text = (
        "Ward,Profcat,Shift,Opp,Indication,HHaction,Missedbutglove,Complied\n"
        "Medical,Nurse,Morning,788,Before patient contact,HW (hand wash),,Yes\n"
        "Medical,Nurse,Morning,788,Before patient contact,,,No\n"
        "Medical,Nurse,Morning,789,After body fluid exposure,HW (hand wash),,Yes\n"
    )
    df = pd.read_csv(io.StringIO(csv_text))
    warnings, can_commit = validate_csv_structure(df)

    codes = [w.code for w in warnings]
    assert "OPP_DUPLICATE" in codes
    assert "TARGET_LEAKAGE_HHACTION" in codes
    assert can_commit is True


def test_missing_column_rejected_with_clear_message():
    csv_text = (
        "Ward,Profcat,Shift,Opp,Indication,HHaction,Complied\n"  # missing Missedbutglove
        "Medical,Nurse,Morning,1,Before patient contact,HW (hand wash),Yes\n"
    )
    df = pd.read_csv(io.StringIO(csv_text))
    with pytest.raises(ValueError) as exc:
        validate_csv_structure(df)
    assert "Missing required columns" in str(exc.value)


def test_unexpected_complied_value_rejected():
    csv_text = (
        "Ward,Profcat,Shift,Opp,Indication,HHaction,Missedbutglove,Complied\n"
        "Medical,Nurse,Morning,1,Before patient contact,HW (hand wash),,Maybe\n"
    )
    df = pd.read_csv(io.StringIO(csv_text))
    with pytest.raises(ValueError) as exc:
        validate_csv_structure(df)
    assert "Unexpected values in Complied column" in str(exc.value)


def test_database_reproduces_published_numbers():
    db = SessionLocal()
    try:
        total = db.query(HandHygieneOpportunity).count()
        complied = db.query(HandHygieneOpportunity).filter(HandHygieneOpportunity.complied == True).count()
        assert total == 917, f"Expected 917, got {total}"
        assert complied == 202, f"Expected 202, got {complied}"
        rate = round((complied / total) * 100, 1)
        assert rate == 22.0
    finally:
        db.close()


def test_sql_query_latency_under_200ms_benchmark():
    db = SessionLocal()
    try:
        # Benchmark summary query
        t0 = time.perf_counter()
        s = analytics.summary(db=db, ward="Medical", shift="Morning", indication="Before patient contact")
        t_elapsed = (time.perf_counter() - t0) * 1000
        assert t_elapsed < 200, f"Query latency too high: {t_elapsed:.2f} ms (KPI requirement: < 200 ms)"
        assert s["opportunities"] > 0

        # Benchmark group query
        t0 = time.perf_counter()
        g = analytics.by_group(db=db, dimension="ward", shift="Morning")
        t_elapsed = (time.perf_counter() - t0) * 1000
        assert t_elapsed < 200, f"Group query latency too high: {t_elapsed:.2f} ms"
        assert len(g["rows"]) == 5

        # Benchmark paginated query
        t0 = time.perf_counter()
        recs = analytics.get_paginated_records(db=db, page=1, page_size=25, ward="Medical")
        t_elapsed = (time.perf_counter() - t0) * 1000
        assert t_elapsed < 200, f"Pagination latency too high: {t_elapsed:.2f} ms"
        assert len(recs["items"]) == 25
    finally:
        db.close()


def test_institutions_and_wards_reference_integrity():
    db = SessionLocal()
    try:
        wards = db.query(Ward).all()
        assert len(wards) == 5
        ward_names = {w.name for w in wards}
        assert ward_names == {"Ob/Gyn", "Paediatric", "Medical", "Surgical", "NICU"}
        for w in wards:
            assert w.institution_id is not None
            assert w.institution.name in ("Debre Berhan referral hospital", "Debre Berhan Referral Hospital")
    finally:
        db.close()
