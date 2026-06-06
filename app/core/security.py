import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.config.constants import UserRole

security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split(":", 1)
        if len(parts) != 2:
            return False
        salt, hash_val = parts
        return hashlib.sha256((salt + plain_password).encode()).hexdigest() == hash_val
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "msg": "Token无效或已过期"}
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "msg": "请先登录"}
        )
    payload = decode_access_token(credentials.credentials)
    return {
        "用户ID": payload.get("用户ID") or payload.get("user_id"),
        "用户名": payload.get("用户名") or payload.get("username"),
        "角色": payload.get("角色") or payload.get("role"),
    }


class RoleChecker:
    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user["角色"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 403, "msg": "权限不足"}
            )
        return current_user


allow_engineer = RoleChecker(UserRole.ENGINEER, UserRole.ADMIN)
allow_supervisor = RoleChecker(UserRole.SUPERVISOR, UserRole.ADMIN)
allow_purchaser = RoleChecker(UserRole.PURCHASER, UserRole.ADMIN)
allow_leader = RoleChecker(UserRole.LEADER, UserRole.ADMIN)
allow_admin = RoleChecker(UserRole.ADMIN)


async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("角色") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 403, "msg": "仅管理员可操作"}
        )
    return current_user
