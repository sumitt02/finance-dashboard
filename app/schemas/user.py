from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.utils.enums import Role

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UpdateRoleRequest(BaseModel):
    role: Role

class UpdateStatusRequest(BaseModel):
    is_active: bool
