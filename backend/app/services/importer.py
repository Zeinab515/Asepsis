import hashlib
import json
import secrets
import pandas as pd
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from app.db.models import DataImport, HandHygieneOpportunity, Institution, User, Ward
from app.schemas.imports import ImportPreviewResponse, ImportWarning

REQUIRED_COLUMNS = ["Ward", "Profcat", "Shift", "Opp", "Indication", "HHaction", "Missedbutglove", "Complied"]
ALLOWED_WARDS = {"Ob/Gyn", "Paediatric", "Medical", "Surgical", "NICU"}
ALLOWED_PROFCATS = {"Nurse", "Medical doctor", "Midwife", "Other"}
ALLOWED_SHIFTS = {"Morning", "After noon", "Night"}
ALLOWED_INDICATIONS = {
    "Before patient contact",
    "Before an aseptic procedure",
    "After patient contact",
    "After contact with patient Surroundings",
    "After body fluid exposure",
}

# Temporary preview store: token -> preview payload & data
_PREVIEW_STORE: Dict[str, Dict] = {}


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_csv_structure(df: pd.DataFrame) -> Tuple[List[ImportWarning], bool]:
    warnings: List[ImportWarning] = []
    can_commit = True

    # Check required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}. Expected exactly: {REQUIRED_COLUMNS}")

    # Check Complied values
    complied_vals = set(df["Complied"].dropna().unique())
    bad_complied = complied_vals - {"Yes", "No"}
    if bad_complied:
        raise ValueError(f"Unexpected values in Complied column: {sorted(bad_complied)}. Allowed: ['Yes', 'No']")

    if df["Complied"].isna().any():
        raise ValueError(f"Complied column cannot contain null values. Found {df['Complied'].isna().sum()} nulls.")

    # 1. Opp sequence check (contract check: 788 duplicate, 787 missing)
    if "Opp" in df.columns:
        opp_series = pd.to_numeric(df["Opp"], errors="coerce")
        dup_opps = opp_series[opp_series.duplicated()].tolist()
        if dup_opps:
            warnings.append(
                ImportWarning(
                    code="OPP_DUPLICATE",
                    message=f"Duplicate observation id(s) detected: {dup_opps}. Stored as-is in source_opp; row_number will be unique key.",
                    severity="warning",
                    affected_count=len(dup_opps),
                )
            )

        min_opp, max_opp = int(opp_series.min()), int(opp_series.max())
        expected_opps = set(range(min_opp, max_opp + 1))
        actual_opps = set(opp_series.dropna().astype(int))
        missing_opps = sorted(list(expected_opps - actual_opps))
        if missing_opps:
            warnings.append(
                ImportWarning(
                    code="OPP_SEQUENCE_GAP",
                    message=f"Sequence gaps in Opp column: missing ids {missing_opps[:10]} (total {len(missing_opps)} missing).",
                    severity="warning",
                    affected_count=len(missing_opps),
                )
            )

    # 2. Target leakage check (HHaction and Missedbutglove)
    is_complied = df["Complied"] == "Yes"
    hhaction_filled_when_no = (df["HHaction"].notna() & (~is_complied)).sum()
    hhaction_empty_when_yes = (df["HHaction"].isna() & is_complied).sum()
    if hhaction_filled_when_no == 0 and hhaction_empty_when_yes == 0:
        warnings.append(
            ImportWarning(
                code="TARGET_LEAKAGE_HHACTION",
                message="Target leakage confirmed: HHaction is populated exactly when Complied='Yes' and empty when 'No'. Barred from model inputs.",
                severity="critical",
                affected_count=len(df),
            )
        )

    mbg_filled_when_yes = (df["Missedbutglove"].notna() & is_complied).sum()
    mbg_empty_when_no = (df["Missedbutglove"].isna() & (~is_complied)).sum()
    if mbg_filled_when_yes == 0 and mbg_empty_when_no == 0:
        warnings.append(
            ImportWarning(
                code="TARGET_LEAKAGE_MISSEDBUTGLOVE",
                message="Target leakage confirmed: Missedbutglove is populated exactly when Complied='No' and empty when 'Yes'. Barred from model inputs.",
                severity="critical",
                affected_count=len(df),
            )
        )

    # 3. Categorical checks
    bad_wards = set(df["Ward"].dropna().unique()) - ALLOWED_WARDS
    if bad_wards:
        raise ValueError(f"Unknown Ward categories: {sorted(bad_wards)}. Allowed: {sorted(ALLOWED_WARDS)}")

    bad_shifts = set(df["Shift"].dropna().unique()) - ALLOWED_SHIFTS
    if bad_shifts:
        raise ValueError(f"Unknown Shift categories: {sorted(bad_shifts)}. Allowed: {sorted(ALLOWED_SHIFTS)}")

    bad_profs = set(df["Profcat"].dropna().unique()) - ALLOWED_PROFCATS
    if bad_profs:
        raise ValueError(f"Unknown Profcat categories: {sorted(bad_profs)}. Allowed: {sorted(ALLOWED_PROFCATS)}")

    bad_indications = set(df["Indication"].dropna().unique()) - ALLOWED_INDICATIONS
    if bad_indications:
        raise ValueError(f"Unknown Indication categories: {sorted(bad_indications)}. Allowed: {sorted(ALLOWED_INDICATIONS)}")

    # 4. Check Ob/Gyn midwife confounding
    ob_midwives = df[(df["Ward"] == "Ob/Gyn") & (df["Profcat"] == "Midwife")]
    other_midwives = df[(df["Ward"] != "Ob/Gyn") & (df["Profcat"] == "Midwife")]
    if len(other_midwives) == 0 and len(ob_midwives) > 0:
        warnings.append(
            ImportWarning(
                code="CONFOUNDING_WARD_PROFCAT",
                message="Confounding alert: All Midwives belong to Ob/Gyn ward. Ward and Profcat cannot be fully disentangled.",
                severity="info",
                affected_count=len(ob_midwives),
            )
        )

    return warnings, can_commit


def preview_csv_import(filename: str, content: bytes) -> ImportPreviewResponse:
    if len(content) > 5 * 1024 * 1024:
        raise ValueError("File size exceeds 5MB limit.")

    sha = compute_sha256(content)
    text_content = content.decode("utf-8", errors="replace")
    df = pd.read_csv(StringIO(text_content))

    if len(df) > 50000:
        raise ValueError(f"Row count ({len(df)}) exceeds limit of 50,000 rows.")

    warnings, can_commit = validate_csv_structure(df)

    complied_count = int((df["Complied"] == "Yes").sum())
    total_count = int(len(df))
    compliance_rate = (complied_count / total_count * 100) if total_count > 0 else 0.0

    preview_token = secrets.token_hex(16)
    sample_rows = df.head(5).to_dict(orient="records")

    # Store in memory for commit step
    _PREVIEW_STORE[preview_token] = {
        "filename": filename,
        "sha256": sha,
        "df": df,
        "warnings": [w.model_dump() for w in warnings],
        "created_at": datetime.utcnow(),
    }

    return ImportPreviewResponse(
        filename=filename,
        sha256=sha,
        row_count=total_count,
        complied_count=complied_count,
        compliance_rate=round(compliance_rate, 2),
        sample_rows=sample_rows,
        warnings=warnings,
        can_commit=can_commit,
        preview_token=preview_token,
    )


def commit_csv_import(
    db: Session,
    preview_token: str,
    imported_by: Optional[Union[str, int]] = None,
    notes: Optional[str] = None,
) -> Tuple[DataImport, int]:
    if preview_token not in _PREVIEW_STORE:
        raise ValueError("Invalid or expired preview token. Please generate a new preview.")

    stored = _PREVIEW_STORE.pop(preview_token)
    df: pd.DataFrame = stored["df"]
    filename = stored["filename"]
    sha256 = stored["sha256"]

    # Resolve imported_by user ID if integer or string username provided
    user_id = None
    if isinstance(imported_by, int):
        user_id = imported_by
    elif isinstance(imported_by, str) and imported_by:
        matched_user = db.query(User).filter_by(username=imported_by).first()
        if matched_user:
            user_id = matched_user.id

    # Package notes and warnings into structured JSON
    notes_payload = {
        "user_notes": notes,
        "warnings": stored["warnings"],
    }
    notes_json = json.dumps(notes_payload)

    # Ensure institution exists
    institution = db.query(Institution).filter(
        (Institution.name == "Debre Berhan referral hospital") | (Institution.name == "Debre Berhan Referral Hospital")
    ).first()
    if not institution:
        institution = Institution(name="Debre Berhan referral hospital")
        db.add(institution)
        db.flush()

    # Ensure wards exist
    ward_cache = {}
    for ward_name in ALLOWED_WARDS:
        ward = db.query(Ward).filter_by(institution_id=institution.id, name=ward_name).first()
        if not ward:
            ward = Ward(institution_id=institution.id, name=ward_name)
            db.add(ward)
            db.flush()
        ward_cache[ward_name] = ward.id

    # Check if duplicate sha256 already committed
    existing_import = db.query(DataImport).filter_by(sha256=sha256).first()
    if existing_import:
        raise ValueError(f"File with SHA-256 hash {sha256[:12]}... has already been imported (import #{existing_import.id}).")

    # Create DataImport record matching PostgreSQL schema
    data_import = DataImport(
        filename=filename,
        sha256=sha256,
        row_count=len(df),
        status="committed",
        imported_by=user_id,
        notes=notes_json,
    )
    db.add(data_import)
    db.flush()

    # Bulk insert opportunities
    opp_objects = []
    for idx, row in df.iterrows():
        opp = HandHygieneOpportunity(
            import_id=data_import.id,
            row_number=idx + 1,
            source_opp=int(row["Opp"]) if pd.notna(row["Opp"]) else None,
            ward_id=ward_cache[row["Ward"]],
            profcat=str(row["Profcat"]),
            shift=str(row["Shift"]),
            indication=str(row["Indication"]),
            hh_action=str(row["HHaction"]) if pd.notna(row["HHaction"]) else None,
            missed_but_glove=str(row["Missedbutglove"]) if pd.notna(row["Missedbutglove"]) else None,
            complied=(row["Complied"] == "Yes"),
        )
        opp_objects.append(opp)

    db.bulk_save_objects(opp_objects)
    db.commit()

    return data_import, len(opp_objects)
