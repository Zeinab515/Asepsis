from typing import List, Optional
from pydantic import BaseModel


class Summary(BaseModel):
    opportunities: int
    actions: int
    compliance_rate: Optional[float]
    ci_low: float
    ci_high: float
    institution: str = "Debre Berhan Referral Hospital"
    notes: Optional[str] = None


class GroupRow(BaseModel):
    group: str
    n: int
    complied: int
    rate: Optional[float]  # None if n < 5 (privacy rate withholding)
    ci_low: float
    ci_high: float
    is_small_sample: bool = False  # True if n < 30
    is_withheld: bool = False  # True if n < 5


class GroupTest(BaseModel):
    name: str
    chi2: float
    dof: int
    p_value: float
    min_expected_count: float
    is_significant: bool


class GroupAnalysis(BaseModel):
    dimension: str
    rows: List[GroupRow]
    test: GroupTest
    note: str
    action_recommendation: Optional[str] = None


class OpportunityRecord(BaseModel):
    id: int
    row_number: int
    source_opp: int
    ward: str
    profcat: str
    shift: str
    indication: str
    complied: bool
    hh_action: Optional[str] = None
    missed_but_glove: Optional[str] = None


class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[OpportunityRecord]
