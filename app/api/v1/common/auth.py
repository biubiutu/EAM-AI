from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, RegisterRequest, RoleAssignRequest
from app.models.user import User
from app.core.database import get_async_session
from app.core.security import hash_password, verify_password, create_access_token, get_current_user, require_admin
from app.config.constants import UserRole


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

        self.router.get(
            "/users",
            response_model=BaseResponse,
            summary="用户列表",
            description="获取所有用户列表（仅管理员）",
            tags=["公共-认证"],
        )(self.list_users)

        return self.router

    async def login(self, request: LoginRequest, session: AsyncSession = Depends(get_async_session)):
        result = await session.execute(select(User).where(User.用户名 == request.username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.密码哈希):
            return BaseResponse(code=401, msg="用户名或密码错误")

        if not user.是否激活:
            return BaseResponse(code=403, msg="账号已被禁用")

        token = create_access_token({
            "user_id": user.id,
            "username": user.用户名,
            "role": user.角色,
        })

        return BaseResponse(data=LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.用户名,
            role=user.角色,
            real_name=user.真实姓名,
        ))

    async def get_me(self, current_user: dict = Depends(get_current_user)):
        return BaseResponse(data=current_user)

    async def register(self, request: RegisterRequest, session: AsyncSession = Depends(get_async_session)):
        result = await session.execute(select(User).where(User.用户名 == request.username))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return BaseResponse(code=400, msg="用户名已存在")

        new_user = User(
            用户名=request.username,
            密码哈希=hash_password(request.password),
            真实姓名=request.real_name,
            邮箱=request.email,
            手机号=request.phone,
            角色="guest",
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return BaseResponse(data={
            "user_id": new_user.id,
            "username": new_user.用户名,
            "role": new_user.角色,
            "message": "注册成功"
        })

    async def assign_role(self, request: RoleAssignRequest, session: AsyncSession = Depends(get_async_session), _=Depends(require_admin)):
        allowed_roles = {
            UserRole.ADMIN,
            UserRole.ENGINEER,
            UserRole.SUPERVISOR,
            UserRole.PURCHASER,
            UserRole.LEADER,
            UserRole.GUEST,
        }
        if request.role not in allowed_roles:
            return BaseResponse(code=400, msg="无效角色")

        result = await session.execute(select(User).where(User.id == request.user_id))
        user = result.scalar_one_or_none()

        if not user:
            return BaseResponse(code=404, msg="用户不存在")

        user.角色 = request.role
        await session.commit()

        return BaseResponse(data={
            "user_id": user.id,
            "username": user.用户名,
            "role": user.角色,
            "message": "角色分配成功"
        })

    async def list_users(self, session: AsyncSession = Depends(get_async_session), _=Depends(require_admin)):
        result = await session.execute(select(User).order_by(User.id))
        users = result.scalars().all()
        data = []
        for u in users:
            data.append({
                "id": u.id,
                "username": u.用户名,
                "real_name": u.真实姓名 or "",
                "email": u.邮箱 or "",
                "phone": u.手机号 or "",
                "role": u.角色,
                "is_active": u.是否激活,
                "created_at": str(u.created_at),
            })
        return BaseResponse(data=data)
