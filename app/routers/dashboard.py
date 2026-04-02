from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import role_required
from app.schemas.dashboard import SummaryResponse, CategoryTotal, MonthlyTrend, RecentRecord
from app.services import dashboard_service
from app.utils.enums import Role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

all_roles      = role_required(Role.viewer, Role.analyst, Role.admin)
analyst_up     = role_required(Role.analyst, Role.admin)

@router.get("/summary", response_model=SummaryResponse)
def summary(db: Session = Depends(get_db), _=Depends(all_roles)):
    """Total income, expenses, and net balance. All roles."""
    return dashboard_service.get_summary(db)

@router.get("/by-category", response_model=list[CategoryTotal])
def by_category(db: Session = Depends(get_db), _=Depends(analyst_up)):
    """Category-wise totals. Analyst and Admin only."""
    return dashboard_service.get_by_category(db)

@router.get("/monthly-trends", response_model=list[MonthlyTrend])
def monthly_trends(db: Session = Depends(get_db), _=Depends(analyst_up)):
    """Income and expense totals for the last 6 months. Analyst and Admin only."""
    return dashboard_service.get_monthly_trends(db)

@router.get("/recent", response_model=list[RecentRecord])
def recent(db: Session = Depends(get_db), _=Depends(all_roles)):
    """Last 5 transactions. All roles."""
    return dashboard_service.get_recent(db)
