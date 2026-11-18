"""Descriptive analytics service for Asepsis / BIOPRESS Analytics.

Ground rules & Honesty requirements:
- Direct database execution using PostgreSQL / SQLite views and indexed tables.
- Every percentage is shown with numerator, denominator and Wilson 95% confidence interval.
- Groups with n below 30 receive a small-sample warning; rates for n below 5 are withheld.
- For Ward, Shift, and Profcat: show "No statistically detectable difference between groups; do not rank them."
- Differences are described as observational associations, never explained as causes.
"""
import math
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from scipy.stats import chi2_contingency
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

GROUP_COLUMNS = {
    "ward": "ward",
    "shift": "shift",
    "profcat": "profcat",
    "indication": "indication",
}


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Calculate the Wilson score 95% confidence interval for a binomial proportion."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ============================================================================
# DATAFRAME FALLBACK IMPLEMENTATION (For ad-hoc datasets / testing)
# ============================================================================

def _filter_dataframe(
    df: pd.DataFrame,
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
) -> pd.DataFrame:
    filtered = df.copy()
    col_map = {c.lower(): c for c in filtered.columns}
    w_col = col_map.get("ward")
    s_col = col_map.get("shift")
    p_col = col_map.get("profcat")
    i_col = col_map.get("indication")

    if ward and w_col:
        filtered = filtered[filtered[w_col] == ward]
    if shift and s_col:
        filtered = filtered[filtered[s_col] == shift]
    if profcat and p_col:
        filtered = filtered[filtered[p_col] == profcat]
    if indication and i_col:
        filtered = filtered[filtered[i_col] == indication]
    return filtered


def _summary_df(
    df: pd.DataFrame,
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
) -> dict:
    f_df = _filter_dataframe(df, ward=ward, shift=shift, profcat=profcat, indication=indication)
    n = int(len(f_df))
    comp_col = "complied" if "complied" in f_df.columns else "Complied"
    if comp_col in f_df.columns:
        if f_df[comp_col].dtype == object:
            k = int((f_df[comp_col] == "Yes").sum())
        else:
            k = int(f_df[comp_col].sum())
    else:
        k = 0

    lo, hi = wilson_ci(k, n)
    rate = (k / n) if n > 0 else None

    notes = []
    if ward or shift or profcat or indication:
        notes.append(f"Filtered subset (n={n}).")
    if n < 30 and n > 0:
        notes.append("Small sample size (n < 30): confidence interval is wide.")

    return {
        "opportunities": n,
        "actions": k,
        "compliance_rate": rate,
        "ci_low": lo if not math.isnan(lo) else 0.0,
        "ci_high": hi if not math.isnan(hi) else 0.0,
        "institution": "Debre Berhan Referral Hospital",
        "notes": " ".join(notes) if notes else "Full audit cohort (Debre Berhan, Ethiopia, 2017).",
    }


def _by_group_df(
    df: pd.DataFrame,
    dimension: str,
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
) -> dict:
    dim_lower = dimension.lower()
    if dim_lower not in GROUP_COLUMNS:
        raise KeyError(f"Invalid dimension: '{dimension}'. Allowed: {list(GROUP_COLUMNS.keys())}")

    col_map = {c.lower(): c for c in df.columns}
    target_col = col_map.get(dim_lower, dim_lower.capitalize())

    f_df = _filter_dataframe(
        df,
        ward=ward if dim_lower != "ward" else None,
        shift=shift if dim_lower != "shift" else None,
        profcat=profcat if dim_lower != "profcat" else None,
        indication=indication if dim_lower != "indication" else None,
    )

    if len(f_df) == 0:
        return {
            "dimension": dim_lower,
            "rows": [],
            "test": {
                "name": "chi-square test of independence",
                "chi2": 0.0,
                "dof": 0,
                "p_value": 1.0,
                "min_expected_count": 0.0,
                "is_significant": False,
            },
            "note": "No observations match active filters.",
            "action_recommendation": "Expand filter selection to view data.",
        }

    comp_col = "complied" if "complied" in f_df.columns else "Complied"
    if comp_col in f_df.columns and f_df[comp_col].dtype == object:
        f_df = f_df.copy()
        f_df["_comp"] = (f_df[comp_col] == "Yes").astype(int)
        sum_col = "_comp"
    else:
        sum_col = comp_col

    g = f_df.groupby(target_col)[sum_col].agg(["sum", "count"]).reset_index()
    rows = []
    for _, r in g.iterrows():
        k, n = int(r["sum"]), int(r["count"])
        lo, hi = wilson_ci(k, n)
        is_withheld = n < 5
        rate = (k / n) if (n > 0 and not is_withheld) else None
        is_small = n < 30

        rows.append({
            "group": str(r[target_col]),
            "n": n,
            "complied": k,
            "rate": rate,
            "ci_low": lo if not math.isnan(lo) else 0.0,
            "ci_high": hi if not math.isnan(hi) else 0.0,
            "is_small_sample": is_small,
            "is_withheld": is_withheld,
        })

    rows.sort(key=lambda x: -x["n"])

    table = pd.crosstab(f_df[target_col], f_df[sum_col])
    if table.shape[0] > 1 and table.shape[1] > 1:
        chi2, p, dof, expected = chi2_contingency(table)
        min_expected = float(expected.min())
    else:
        chi2, p, dof, min_expected = 0.0, 1.0, 0, 0.0

    is_significant = bool(p < 0.05)
    if is_significant:
        verdict = "Overall difference between groups is statistically detectable."
        action = "Prioritize workflow support for indications where compliance is systematically lower."
    else:
        verdict = "No statistically detectable difference between groups; do not rank them."
        action = "Do not treat observed group differences as meaningful or rank departments/shifts."

    return {
        "dimension": dim_lower,
        "rows": rows,
        "test": {
            "name": "chi-square test of independence",
            "chi2": float(chi2),
            "dof": int(dof),
            "p_value": float(p),
            "min_expected_count": float(min_expected),
            "is_significant": is_significant,
        },
        "note": f"Descriptive only; differences are not evidence of a cause. {verdict}",
        "action_recommendation": action,
    }


# ============================================================================
# DATABASE-BACKED IMPLEMENTATION (Primary Production / Track B)
# ============================================================================

def summary(
    db_or_df: Optional[Union[Session, pd.DataFrame]] = None,
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Compute summary statistics directly from v_compliance_facts or dataframe."""
    target_session = db if db is not None else (db_or_df if isinstance(db_or_df, Session) else None)

    if isinstance(db_or_df, pd.DataFrame):
        return _summary_df(db_or_df, ward=ward, shift=shift, profcat=profcat, indication=indication)

    close_session_later = False
    if target_session is None:
        target_session = SessionLocal()
        close_session_later = True

    try:
        query = text("""
            SELECT 
                COALESCE(SUM(n), 0) AS opportunities,
                COALESCE(SUM(complied_count), 0) AS actions
            FROM v_compliance_facts
            WHERE (:ward IS NULL OR ward = :ward)
              AND (:shift IS NULL OR shift = :shift)
              AND (:profcat IS NULL OR profcat = :profcat)
              AND (:indication IS NULL OR indication = :indication)
        """)
        row = target_session.execute(
            query,
            {"ward": ward, "shift": shift, "profcat": profcat, "indication": indication},
        ).fetchone()

        n = int(row[0]) if row else 0
        k = int(row[1]) if row else 0
        lo, hi = wilson_ci(k, n)
        rate = (k / n) if n > 0 else None

        notes = []
        if ward or shift or profcat or indication:
            notes.append(f"Filtered subset (n={n}).")
        if n < 30 and n > 0:
            notes.append("Small sample size (n < 30): confidence interval is wide.")

        return {
            "opportunities": n,
            "actions": k,
            "compliance_rate": rate,
            "ci_low": lo if not math.isnan(lo) else 0.0,
            "ci_high": hi if not math.isnan(hi) else 0.0,
            "institution": "Debre Berhan Referral Hospital",
            "notes": " ".join(notes) if notes else "Full audit cohort (Debre Berhan, Ethiopia, 2017).",
        }
    finally:
        if close_session_later:
            target_session.close()


def by_group(
    db_or_df: Optional[Union[Session, pd.DataFrame]] = None,
    dimension: str = "ward",
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Compute subgroup compliance rates with Wilson 95% CIs and chi-square test."""
    target_session = db if db is not None else (db_or_df if isinstance(db_or_df, Session) else None)

    if isinstance(db_or_df, pd.DataFrame):
        return _by_group_df(db_or_df, dimension, ward=ward, shift=shift, profcat=profcat, indication=indication)

    dim_lower = dimension.lower()
    if dim_lower not in GROUP_COLUMNS:
        raise KeyError(f"Invalid dimension: '{dimension}'. Allowed: {list(GROUP_COLUMNS.keys())}")

    target_col = GROUP_COLUMNS[dim_lower]

    close_session_later = False
    if target_session is None:
        target_session = SessionLocal()
        close_session_later = True

    try:
        # Exclude active dimension from filters to aggregate all its categories
        filter_ward = ward if dim_lower != "ward" else None
        filter_shift = shift if dim_lower != "shift" else None
        filter_profcat = profcat if dim_lower != "profcat" else None
        filter_indication = indication if dim_lower != "indication" else None

        sql = f"""
            SELECT 
                {target_col} AS group_name,
                COALESCE(SUM(n), 0) AS n,
                COALESCE(SUM(complied_count), 0) AS complied_count
            FROM v_compliance_facts
            WHERE (:ward IS NULL OR ward = :ward)
              AND (:shift IS NULL OR shift = :shift)
              AND (:profcat IS NULL OR profcat = :profcat)
              AND (:indication IS NULL OR indication = :indication)
            GROUP BY {target_col}
            ORDER BY n DESC;
        """
        result = target_session.execute(
            text(sql),
            {
                "ward": filter_ward,
                "shift": filter_shift,
                "profcat": filter_profcat,
                "indication": filter_indication,
            },
        ).fetchall()

        rows = []
        for r in result:
            group_name = str(r[0])
            n = int(r[1])
            k = int(r[2])
            lo, hi = wilson_ci(k, n)

            is_withheld = n < 5
            rate = (k / n) if (n > 0 and not is_withheld) else None
            is_small = n < 30

            rows.append({
                "group": group_name,
                "n": n,
                "complied": k,
                "rate": rate,
                "ci_low": lo if not math.isnan(lo) else 0.0,
                "ci_high": hi if not math.isnan(hi) else 0.0,
                "is_small_sample": is_small,
                "is_withheld": is_withheld,
            })

        if not rows:
            return {
                "dimension": dim_lower,
                "rows": [],
                "test": {
                    "name": "chi-square test of independence",
                    "chi2": 0.0,
                    "dof": 0,
                    "p_value": 1.0,
                    "min_expected_count": 0.0,
                    "is_significant": False,
                },
                "note": "No observations match active filters.",
                "action_recommendation": "Expand filter selection to view data.",
            }

        # Contingency table for Chi-Square test: each row has [complied, non_complied]
        contingency_table = [[r["complied"], r["n"] - r["complied"]] for r in rows if r["n"] > 0]
        if (
            len(contingency_table) > 1
            and sum(row[0] for row in contingency_table) > 0
            and sum(row[1] for row in contingency_table) > 0
        ):
            chi2, p, dof, expected = chi2_contingency(contingency_table)
            min_expected = float(expected.min())
        else:
            chi2, p, dof, min_expected = 0.0, 1.0, 0, 0.0

        is_significant = bool(p < 0.05)
        if is_significant:
            verdict = "Overall difference between groups is statistically detectable."
            action = "Prioritize workflow support for indications where compliance is systematically lower."
        else:
            verdict = "No statistically detectable difference between groups; do not rank them."
            action = "Do not treat observed group differences as meaningful or rank departments/shifts."

        return {
            "dimension": dim_lower,
            "rows": rows,
            "test": {
                "name": "chi-square test of independence",
                "chi2": float(chi2),
                "dof": int(dof),
                "p_value": float(p),
                "min_expected_count": float(min_expected),
                "is_significant": is_significant,
            },
            "note": f"Descriptive only; differences are not evidence of a cause. {verdict}",
            "action_recommendation": action,
        }
    finally:
        if close_session_later:
            target_session.close()


def get_paginated_records(
    db_or_df: Optional[Union[Session, pd.DataFrame]] = None,
    page: int = 1,
    page_size: int = 25,
    ward: Optional[str] = None,
    shift: Optional[str] = None,
    profcat: Optional[str] = None,
    indication: Optional[str] = None,
    search: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Retrieve paginated opportunities directly from database with SQL filters."""
    target_session = db if db is not None else (db_or_df if isinstance(db_or_df, Session) else None)

    if isinstance(db_or_df, pd.DataFrame):
        # Fallback for dataframe
        f_df = _filter_dataframe(db_or_df, ward=ward, shift=shift, profcat=profcat, indication=indication)
        if search:
            s = search.lower()
            mask = (
                f_df["Ward"].str.lower().str.contains(s)
                | f_df["Profcat"].str.lower().str.contains(s)
                | f_df["Shift"].str.lower().str.contains(s)
                | f_df["Indication"].str.lower().str.contains(s)
            )
            f_df = f_df[mask]
        total = len(f_df)
        total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * page_size
        slice_df = f_df.iloc[start_idx : start_idx + page_size]
        items = []
        for idx, r in slice_df.iterrows():
            items.append({
                "id": int(idx) + 1,
                "row_number": int(idx) + 1,
                "source_opp": int(r["Opp"]) if "Opp" in r and pd.notna(r["Opp"]) else int(idx) + 1,
                "ward": str(r["Ward"]),
                "profcat": str(r["Profcat"]),
                "shift": str(r["Shift"]),
                "indication": str(r["Indication"]),
                "complied": bool(r.get("Complied") == "Yes" or r.get("complied") == 1),
                "hh_action": str(r["HHaction"]) if pd.notna(r.get("HHaction")) else None,
                "missed_but_glove": str(r["Missedbutglove"]) if pd.notna(r.get("Missedbutglove")) else None,
            })
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
        }

    close_session_later = False
    if target_session is None:
        target_session = SessionLocal()
        close_session_later = True

    try:
        search_param = f"%{search.lower()}%" if search else None

        count_sql = text("""
            SELECT COUNT(*)
            FROM hand_hygiene_opportunities o
            JOIN wards w ON o.ward_id = w.id
            JOIN data_imports i ON o.import_id = i.id
            WHERE i.status = 'committed'
              AND (:ward IS NULL OR w.name = :ward)
              AND (:shift IS NULL OR o.shift = :shift)
              AND (:profcat IS NULL OR o.profcat = :profcat)
              AND (:indication IS NULL OR o.indication = :indication)
              AND (:search IS NULL OR (
                  LOWER(w.name) LIKE :search OR
                  LOWER(o.profcat) LIKE :search OR
                  LOWER(o.shift) LIKE :search OR
                  LOWER(o.indication) LIKE :search
              ))
        """)
        total = target_session.execute(
            count_sql,
            {
                "ward": ward,
                "shift": shift,
                "profcat": profcat,
                "indication": indication,
                "search": search_param,
            },
        ).scalar() or 0

        total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size

        select_sql = text("""
            SELECT 
                o.id,
                o.row_number,
                o.source_opp,
                w.name AS ward,
                o.profcat,
                o.shift,
                o.indication,
                o.complied,
                o.hh_action,
                o.missed_but_glove
            FROM hand_hygiene_opportunities o
            JOIN wards w ON o.ward_id = w.id
            JOIN data_imports i ON o.import_id = i.id
            WHERE i.status = 'committed'
              AND (:ward IS NULL OR w.name = :ward)
              AND (:shift IS NULL OR o.shift = :shift)
              AND (:profcat IS NULL OR o.profcat = :profcat)
              AND (:indication IS NULL OR o.indication = :indication)
              AND (:search IS NULL OR (
                  LOWER(w.name) LIKE :search OR
                  LOWER(o.profcat) LIKE :search OR
                  LOWER(o.shift) LIKE :search OR
                  LOWER(o.indication) LIKE :search
              ))
            ORDER BY o.row_number ASC
            LIMIT :limit OFFSET :offset;
        """)
        rows = target_session.execute(
            select_sql,
            {
                "ward": ward,
                "shift": shift,
                "profcat": profcat,
                "indication": indication,
                "search": search_param,
                "limit": page_size,
                "offset": offset,
            },
        ).fetchall()

        items = []
        for r in rows:
            items.append({
                "id": int(r[0]),
                "row_number": int(r[1]),
                "source_opp": int(r[2]) if r[2] is not None else int(r[1]),
                "ward": str(r[3]),
                "profcat": str(r[4]),
                "shift": str(r[5]),
                "indication": str(r[6]),
                "complied": bool(r[7]),
                "hh_action": str(r[8]) if r[8] is not None else None,
                "missed_but_glove": str(r[9]) if r[9] is not None else None,
            })

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
        }
    finally:
        if close_session_later:
            target_session.close()


def filter_dataframe(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Helper for backwards compatibility with existing callers."""
    return _filter_dataframe(df, **kwargs)
