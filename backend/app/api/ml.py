import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_optional
from app.db.models import ModelRun, User
from app.db.session import get_db
from app.ml import evaluate
from app.schemas.ml import EvaluationReportResponse, PredictRequest, PredictResponse

router = APIRouter(prefix="/api/v1/ml", tags=["Machine Learning & XAI"])


@router.get("/evaluation", response_model=EvaluationReportResponse)
def get_evaluation():
    try:
        report = evaluate.get_cached_or_run_report()
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}",
        )


@router.post("/train", response_model=EvaluationReportResponse)
def trigger_training(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Trigger reproducible ML benchmark and persist run in database."""
    try:
        report = evaluate.run_full_ml_benchmark()

        # Record in model_runs table matching PostgreSQL schema
        run_record = ModelRun(
            model_type="LogisticRegression_vs_Baselines",
            git_commit=report["git_commit"],
            features=["ward", "profcat", "shift", "indication"],
            metrics={
                "baseline_compliance": report["baseline_compliance_rate"],
                "benchmarks_count": len(report["benchmark_table"]),
                "odds_ratios_count": len(report["odds_ratios"]),
            },
            artifact_path=str(evaluate.REPORT_FILE),
        )
        db.add(run_record)
        db.commit()

        return report
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}",
        )


@router.post("/explain", response_model=PredictResponse)
def explain_opportunity(req: PredictRequest):
    try:
        return evaluate.explain_single_opportunity(
            ward=req.ward,
            profcat=req.profcat,
            shift=req.shift,
            indication=req.indication,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction explanation failed: {str(e)}",
        )


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(ModelRun).order_by(ModelRun.created_at.desc()).limit(20).all()
    out = []
    for r in runs:
        feat = r.features if isinstance(r.features, (list, dict)) else json.loads(r.features or "[]")
        met = r.metrics if isinstance(r.metrics, (list, dict)) else json.loads(r.metrics or "{}")
        out.append({
            "id": r.id,
            "created_at": r.created_at,
            "model_type": r.model_type,
            "git_commit": r.git_commit,
            "features": feat,
            "metrics": met,
            "artifact_path": r.artifact_path,
        })
    return out
