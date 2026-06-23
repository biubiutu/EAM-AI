"""创建或重置管理员账号。用法: python -m app.create_admin"""
import asyncio

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


async def main() -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.用户名 == ADMIN_USERNAME)
        )
        user = result.scalar_one_or_none()
        if user:
            user.密码哈希 = hash_password(ADMIN_PASSWORD)
            user.角色 = "admin"
            user.是否激活 = True
            action = "已重置密码"
        else:
            session.add(
                User(
                    用户名=ADMIN_USERNAME,
                    密码哈希=hash_password(ADMIN_PASSWORD),
                    真实姓名="系统管理员",
                    邮箱="admin@eam.com",
                    手机号="13800000001",
                    角色="admin",
                    是否激活=True,
                )
            )
            action = "已创建"
        await session.commit()
        print(f"[OK] 管理员{action}")
        print(f"     用户名: {ADMIN_USERNAME}")
        print(f"     密码:   {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
