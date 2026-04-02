from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from app.utils.enums import RecordType

class RecordCreateRequest(BaseModel):
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip()

class RecordUpdateRequest(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    is_deleted: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
