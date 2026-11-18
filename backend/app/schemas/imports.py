from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ImportWarning(BaseModel):
    code: str
    message: str
    severity: str  # 'warning', 'info', 'critical'
    affected_count: int = 0


class ImportPreviewResponse(BaseModel):
    filename: str
    sha256: str
    row_count: int
    complied_count: int
    compliance_rate: float
    sample_rows: List[Dict[str, Any]]
    warnings: List[ImportWarning]
    can_commit: bool
    preview_token: str


class ImportCommitRequest(BaseModel):
    preview_token: str
    notes: Optional[str] = None


class ImportCommitResponse(BaseModel):
    import_id: int
    filename: str
    row_count: int
    status: str
    warnings_count: int
    message: str


class ImportHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    sha256: str
    row_count: int
    status: str
    imported_by: str
    imported_at: datetime
    notes: Optional[str] = None
    warnings: List[str] = []
