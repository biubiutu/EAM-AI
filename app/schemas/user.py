from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str
    real_name: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "engineer"


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class RoleAssignRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")
    role: str = Field(..., description="角色：engineer/supervisor/purchaser/leader")