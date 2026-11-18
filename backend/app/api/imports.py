import json
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_optional
from app.db.models import AuditLog, DataImport, User
from app.db.session import get_db
from app.schemas.imports import ImportCommitRequest, ImportCommitResponse, ImportHistoryItem, ImportPreviewResponse
from app.services import importer

router = APIRouter(prefix="/api/v1/imports", tags=["Data Import Pipeline"])


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_csv(file: UploadFile = File(...)):
    """Preview uploaded audit CSV with automated schema validation and leakage detection."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .csv file.",
        )

    try:
        content = await file.read()
        return importer.preview_csv_import(filename=file.filename, content=content)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Import preview failed: {str(e)}")


@router.post("/commit", response_model=ImportCommitResponse)
def commit_csv(
    req: ImportCommitRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Commit validated preview opportunities to the relational database."""
    username = current_user.username if current_user else "system"
    user_id = current_user.id if current_user else None
    try:
        data_import, row_count = importer.commit_csv_import(
            db=db,
            preview_token=req.preview_token,
            imported_by=user_id if user_id else username,
            notes=req.notes,
        )

        # Record in audit log matching PostgreSQL schema
        audit = AuditLog(
            user_id=user_id,
            username=username,
            action="import_csv",
            resource="data_import",
            details={"filename": data_import.filename, "rows": row_count, "import_id": data_import.id},
        )
        db.add(audit)
        db.commit()

        warnings_list = json.loads(data_import.warnings or "[]")
        return ImportCommitResponse(
            import_id=data_import.id,
            filename=data_import.filename,
            row_count=row_count,
            status=data_import.status,
            warnings_count=len(warnings_list),
            message=f"Successfully imported {row_count} opportunities from {data_import.filename}.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Commit failed: {str(e)}")


@router.get("/history", response_model=List[ImportHistoryItem])
def get_import_history(db: Session = Depends(get_db)):
    """Retrieve history of committed data imports and audit warnings."""
    imports = db.query(DataImport).order_by(DataImport.imported_at.desc()).all()
    results = []
    for item in imports:
        warns = json.loads(item.warnings or "[]")
        warn_msgs = [w.get("message", str(w)) if isinstance(w, dict) else str(w) for w in warns]
        imported_by_str = item.user.username if item.user else "system"
        results.append(
            ImportHistoryItem(
                id=item.id,
                filename=item.filename,
                sha256=item.sha256,
                row_count=item.row_count,
                status=item.status,
                imported_by=imported_by_str,
                imported_at=item.imported_at,
                notes=item.notes,
                warnings=warn_msgs,
            )
        )
    return results
