from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import GroupAnalysis, PaginatedRecords, Summary
from app.services import analytics

router = APIRouter(prefix="/api/v1/analytics", tags=["Descriptive Analytics"])


@router.get("/summary", response_model=Summary)
def get_summary(
    ward: Optional[str] = Query(None, description="Filter by Ward"),
    shift: Optional[str] = Query(None, description="Filter by Shift"),
    profcat: Optional[str] = Query(None, description="Filter by Professional Category"),
    indication: Optional[str] = Query(None, description="Filter by WHO Hand Hygiene Indication"),
    db: Session = Depends(get_db),
):
    """Get overall compliance summary with exact sample size and Wilson 95% CI.
    Queries database view v_compliance_facts directly.
    """
    return analytics.summary(db=db, ward=ward, shift=shift, profcat=profcat, indication=indication)


@router.get("/by-ward", response_model=GroupAnalysis)
def get_by_ward(
    shift: Optional[str] = Query(None),
    profcat: Optional[str] = Query(None),
    indication: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Analyze compliance across wards with chi-square significance testing."""
    return analytics.by_group(db=db, dimension="ward", shift=shift, profcat=profcat, indication=indication)


@router.get("/by-shift", response_model=GroupAnalysis)
def get_by_shift(
    ward: Optional[str] = Query(None),
    profcat: Optional[str] = Query(None),
    indication: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Analyze compliance across shifts with chi-square significance testing."""
    return analytics.by_group(db=db, dimension="shift", ward=ward, profcat=profcat, indication=indication)


@router.get("/by-indication", response_model=GroupAnalysis)
def get_by_indication(
    ward: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    profcat: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Analyze compliance across WHO '5 Moments' indications."""
    return analytics.by_group(db=db, dimension="indication", ward=ward, shift=shift, profcat=profcat)


@router.get("/by-profcat", response_model=GroupAnalysis)
def get_by_profcat(
    ward: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    indication: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Analyze compliance across professional categories."""
    return analytics.by_group(db=db, dimension="profcat", ward=ward, shift=shift, indication=indication)


@router.get("/records", response_model=PaginatedRecords)
def get_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    ward: Optional[str] = Query(None),
    shift: Optional[str] = Query(None),
    profcat: Optional[str] = Query(None),
    indication: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get paginated individual observation opportunities directly from SQL database."""
    return analytics.get_paginated_records(
        db=db,
        page=page,
        page_size=page_size,
        ward=ward,
        shift=shift,
        profcat=profcat,
        indication=indication,
        search=search,
    )
