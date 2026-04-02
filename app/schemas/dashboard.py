from pydantic import BaseModel
from typing import List

class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float

class CategoryTotal(BaseModel):
    category: str
    total: float
    type: str

class MonthlyTrend(BaseModel):
    month: str   # e.g. "2024-03"
    income: float
    expense: float

class RecentRecord(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: str
    notes: str | None
