from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from typing import Optional
from app.models.record import FinancialRecord
from app.schemas.record import RecordCreateRequest, RecordUpdateRequest
from app.utils.exceptions import NotFoundException
from app.utils.enums import RecordType

def create_record(data: RecordCreateRequest, user_id: int, db: Session) -> FinancialRecord:
    record = FinancialRecord(
        amount=data.amount,
        type=data.type.value,
        category=data.category,
        date=data.date,
        notes=data.notes,
        created_by=user_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_records(
    db: Session,
    record_type: Optional[RecordType] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 20
) -> list[FinancialRecord]:
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if record_type:
        query = query.filter(FinancialRecord.type == record_type.value)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    return query.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit).all()

def get_record_by_id(record_id: int, db: Session) -> FinancialRecord:
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()
    if not record:
        raise NotFoundException(f"Record with id {record_id} not found")
    return record

def update_record(record_id: int, data: RecordUpdateRequest, db: Session) -> FinancialRecord:
    record = get_record_by_id(record_id, db)

    if data.amount is not None:
        record.amount = data.amount
    if data.type is not None:
        record.type = data.type.value
    if data.category is not None:
        record.category = data.category
    if data.date is not None:
        record.date = data.date
    if data.notes is not None:
        record.notes = data.notes

    db.commit()
    db.refresh(record)
    return record

def soft_delete_record(record_id: int, db: Session) -> dict:
    record = get_record_by_id(record_id, db)
    record.is_deleted = True
    db.commit()
    return {"message": f"Record {record_id} deleted successfully"}
