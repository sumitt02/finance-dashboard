from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import role_required
from app.schemas.record import RecordCreateRequest, RecordUpdateRequest, RecordResponse
from app.services import record_service
from app.utils.enums import Role, RecordType

router = APIRouter(prefix="/records", tags=["Records"])

all_roles = role_required(Role.viewer, Role.analyst, Role.admin)
admin_only = role_required(Role.admin)

@router.post("/", response_model=RecordResponse, status_code=201)
def create_record(
    data: RecordCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(admin_only)
):
    """Create a new financial record. Admin only."""
    return record_service.create_record(data, current_user.id, db)

@router.get("/", response_model=list[RecordResponse])
def list_records(
    record_type: Optional[RecordType] = Query(None, alias="type"),
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(all_roles)
):
    """
    List financial records with optional filters.
    Supports: type, category, date_from, date_to, pagination.
    Viewer, Analyst, Admin.
    """
    return record_service.get_records(db, record_type, category, date_from, date_to, skip, limit)

@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _=Depends(all_roles)
):
    """Get a single record by ID. Viewer, Analyst, Admin."""
    return record_service.get_record_by_id(record_id, db)

@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """Update a record. Admin only."""
    return record_service.update_record(record_id, data, db)

@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """Soft delete a record. Admin only."""
    return record_service.soft_delete_record(record_id, db)
