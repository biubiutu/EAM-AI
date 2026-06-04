from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, RegisterRequest, RoleAssignRequest
from app.models.user import User
from app.core.database import get_async_session
from app.core.security import hash_password, verify_password, create_access_token, get_current_user, require_admin


class AuthRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/login",
            response_model=BaseResponse[LoginResponse],
            summary="用户登录",
            description="使用用户名和密码登录系统，返回 JWT Token",
            tags=["公共-认证"],
        )(self.login)

        self.router.post(
            "/register",
            response_model=BaseResponse,
            summary="用户注册",
            description="新用户注册账号，默认角色为工程师，管理员可分配其他角色",
            tags=["公共-认证"],
        )(self.register)

        self.router.get(
            "/me",
            response_model=BaseResponse,
            summary="获取当前用户信息",
            description="根据 JWT Token 获取当前登录用户的详细信息",
            tags=["公共-认证"],
        )(self.get_me)

        self.router.post(
            "/assign-role",
            response_model=BaseResponse,
            summary="分配用户角色",
            description="管理员为用户分配或修改角色权限",
            tags=["公共-认证"],
        )(self.assign_role)

        return self.router

    async def login(self, request: LoginRequest, session: AsyncSession = Depends(get_async_session)):
        result = await session.execute(select(User).where(User.username == request.username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.password_hash):
            return BaseResponse(code=401, msg="用户名或密码错误")

        if not user.is_active:
            return BaseResponse(code=403, msg="账号已被禁用")

        token = create_access_token({
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
        })

        return BaseResponse(data=LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            role=user.role,
            real_name=user.real_name,
        ))

    async def get_me(self, current_user: dict = Depends(get_current_user)):
        return BaseResponse(data=current_user)

    async def register(self, request: RegisterRequest, session: AsyncSession = Depends(get_async_session)):
        result = await session.execute(select(User).where(User.username == request.username))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return BaseResponse(code=400, msg="用户名已存在")

        new_user = User(
            username=request.username,
            password_hash=hash_password(request.password),
            real_name=request.real_name,
            email=request.email,
            phone=request.phone,
            role="guest",
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return BaseResponse(data={
            "user_id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
            "message": "注册成功"
        })

    async def assign_role(self, request: RoleAssignRequest, session: AsyncSession = Depends(get_async_session), _=Depends(require_admin)):
        result = await session.execute(select(User).where(User.id == request.user_id))
        user = result.scalar_one_or_none()

        if not user:
            return BaseResponse(code=404, msg="用户不存在")

        user.role = request.role
        await session.commit()

        return BaseResponse(data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "message": "角色分配成功"
        })
