"""
操作审计日志服务
"""
from datetime import datetime
from app.core.database import async_session_factory
from app.models.audit_log import AuditLog


class AuditService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    async def log(self, user_id: int, username: str, action_type: str, detail: str, ip: str = ""):
        """记录审计日志"""
        import json
        async with async_session_factory() as session:
            log = AuditLog(
                用户ID=user_id,
                用户名=username,
                操作类型=action_type,
                操作详情=detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False),
                IP地址=ip,
            )
            session.add(log)
            await session.commit()

    async def get_logs(self, page: int = 1, page_size: int = 50, action_type: str = "") -> dict:
        from sqlalchemy import select, func, desc
        async with async_session_factory() as session:
            stmt = select(AuditLog).order_by(desc(AuditLog.id))
            count_stmt = select(func.count()).select_from(AuditLog)
            if action_type:
                stmt = stmt.where(AuditLog.操作类型 == action_type)
                count_stmt = count_stmt.where(AuditLog.操作类型 == action_type)
            total = (await session.execute(count_stmt)).scalar() or 0
            offset = (page - 1) * page_size
            result = await session.execute(stmt.offset(offset).limit(page_size))
            items = result.scalars().all()
            return {
                "items": [{
                    "id": item.id,
                    "用户ID": item.用户ID,
                    "用户名": item.用户名,
                    "操作类型": item.操作类型,
                    "操作详情": item.操作详情,
                    "IP地址": item.IP地址,
                    "时间": str(item.created_at),
                } for item in items],
                "total": total,
            }


audit_service = AuditService()