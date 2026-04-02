from fastapi import Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.utils.exceptions import UnauthorizedException, ForbiddenException
from app.utils.enums import Role

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ForbiddenException("Your account is deactivated")

    return user

def role_required(*roles: Role):
    """Dependency factory — restricts route to specified roles."""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in roles]:
            raise ForbiddenException(
                f"Access denied. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    return checker
