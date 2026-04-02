from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UpdateRoleRequest, UpdateStatusRequest
from app.utils.exceptions import NotFoundException

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    return user

def update_user_role(user_id: int, data: UpdateRoleRequest, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    user.role = data.role.value
    db.commit()
    db.refresh(user)
    return user

def update_user_status(user_id: int, data: UpdateStatusRequest, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user
