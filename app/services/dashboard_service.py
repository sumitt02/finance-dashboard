from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.models.record import FinancialRecord
from app.schemas.dashboard import SummaryResponse, CategoryTotal, MonthlyTrend, RecentRecord

def get_summary(db: Session) -> SummaryResponse:
    rows = db.query(
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(
        FinancialRecord.is_deleted == False
    ).group_by(FinancialRecord.type).all()

    totals = {row.type: row.total for row in rows}
    income = totals.get("income", 0.0)
    expense = totals.get("expense", 0.0)
    
    return SummaryResponse(
    total_income=round(income, 2),
    total_expenses=round(expense, 2),
    net_balance=round(income - expense, 2)
)

def get_by_category(db: Session) -> list[CategoryTotal]:
    rows = db.query(
        FinancialRecord.category,
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(
        FinancialRecord.is_deleted == False
    ).group_by(FinancialRecord.category, FinancialRecord.type).all()

    return [
        CategoryTotal(category=row.category, type=row.type, total=round(row.total, 2))
        for row in rows
    ]

def get_monthly_trends(db: Session) -> list[MonthlyTrend]:
    # Last 6 months
    today = date.today()
    six_months_ago = today - timedelta(days=180)

    rows = db.query(
        func.strftime("%Y-%m", FinancialRecord.date).label("month"),
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(
        FinancialRecord.is_deleted == False,
        FinancialRecord.date >= six_months_ago
    ).group_by("month", FinancialRecord.type).order_by("month").all()

    # Build a dict keyed by month
    trend_map: dict[str, dict] = {}
    for row in rows:
        if row.month not in trend_map:
            trend_map[row.month] = {"income": 0.0, "expense": 0.0}
        trend_map[row.month][row.type] = round(row.total, 2)

    return [
        MonthlyTrend(month=month, income=data["income"], expense=data["expense"])
        for month, data in sorted(trend_map.items())
    ]

def get_recent(db: Session) -> list[RecentRecord]:
    records = db.query(FinancialRecord).filter(
        FinancialRecord.is_deleted == False
    ).order_by(FinancialRecord.date.desc()).limit(5).all()

    return [
        RecentRecord(
            id=r.id,
            amount=r.amount,
            type=r.type,
            category=r.category,
            date=str(r.date),
            notes=r.notes
        )
        for r in records
    ]
