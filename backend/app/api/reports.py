import io
import csv
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.security import sanitize_csv_cell
from app.db.session import get_db
from app.services import analytics

router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Export"])


@router.get("/summary")
def get_report_summary(db: Session = Depends(get_db)):
    """Generate formal IPC compliance audit report summary from database."""
    overall = analytics.summary(db=db)
    by_ward = analytics.by_group(db=db, dimension="ward")
    by_shift = analytics.by_group(db=db, dimension="shift")
    by_prof = analytics.by_group(db=db, dimension="profcat")
    by_ind = analytics.by_group(db=db, dimension="indication")

    return {
        "title": "Hospital Hand Hygiene Compliance Audit Report",
        "institution": "Debre Berhan Referral Hospital",
        "period": "Cross-Sectional Observational Audit (2017)",
        "source": "Kolola & Gezahegn (2017)",
        "overall": overall,
        "dimensions": {
            "indication": by_ind,
            "ward": by_ward,
            "shift": by_shift,
            "profcat": by_prof,
        },
        "statistical_conclusion": (
            "Indication is the only dimension with a statistically detectable association with compliance (p < 0.001). "
            "Differences between Wards (p=0.21), Shifts (p=0.59), and Professional Categories (p=0.89) are not statistically significant."
        ),
        "limitations": [
            "Single hospital observational audit data; cannot be generalized to other healthcare facilities.",
            "Hawthorne effect: direct observation is known to temporarily raise compliance above everyday baseline.",
            "Absence of worker IDs, patient IDs, and observation session IDs means observations may be clustered.",
            "Strict policy: Audit results describe system-level opportunity patterns and must never be used to rank or discipline individual staff.",
        ],
    }


@router.get("/export-csv")
def export_sanitized_csv(
    ward: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    profcat: Optional[str] = Query(None),
    indication: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Download sanitized CSV of filtered audit opportunities directly from database.

    Cells starting with '=', '+', '-', or '@' are escaped to prevent formula injection.
    """
    sql = text("""
        SELECT 
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
        ORDER BY o.row_number ASC;
    """)
    rows = db.execute(
        sql,
        {"ward": ward, "shift": shift, "profcat": profcat, "indication": indication},
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    headers = ["Row", "Opp", "Ward", "Profcat", "Shift", "Indication", "Complied", "HHaction", "Missedbutglove"]
    writer.writerow(headers)

    for r in rows:
        complied_str = "Yes" if r[6] else "No"
        writer.writerow([
            sanitize_csv_cell(r[0]),
            sanitize_csv_cell(r[1] if r[1] is not None else r[0]),
            sanitize_csv_cell(r[2]),
            sanitize_csv_cell(r[3]),
            sanitize_csv_cell(r[4]),
            sanitize_csv_cell(r[5]),
            sanitize_csv_cell(complied_str),
            sanitize_csv_cell(r[7] if r[7] is not None else ""),
            sanitize_csv_cell(r[8] if r[8] is not None else ""),
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asepsis_hand_hygiene_export.csv"},
    )
