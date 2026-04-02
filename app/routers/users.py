from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import role_required
from app.schemas.user import UserResponse, UpdateRoleRequest, UpdateStatusRequest
from app.services import user_service
from app.utils.enums import Role

router = APIRouter(prefix="/users", tags=["Users"])

# All user management routes are admin only
admin_only = role_required(Role.admin)

@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _=Depends(admin_only)):
    """List all users. Admin only."""
    return user_service.get_all_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    """Get a single user by ID. Admin only."""
    return user_service.get_user_by_id(user_id, db)

@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: int,
    data: UpdateRoleRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """Update a user's role. Admin only."""
    return user_service.update_user_role(user_id, data, db)

@router.patch("/{user_id}/status", response_model=UserResponse)
def update_status(
    user_id: int,
    data: UpdateStatusRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    """Activate or deactivate a user. Admin only."""
    return user_service.update_user_status(user_id, data, db)
