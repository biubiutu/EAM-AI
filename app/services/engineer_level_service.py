"""
工程师等级进阶服务
"""
import logging
from sqlalchemy import select, func
from app.core.database import async_session_factory
from app.models.user import User, ExamRecord, SkillRecord
from app.models.work_order import WorkOrder
from app.config.constants import EngineerLevel

logger = logging.getLogger(__name__)

# 进阶规则
_PROMOTION_RULES = {
    EngineerLevel.INTERMEDIATE: {"min_avg_score": 75, "min_exp": 50, "min_work_orders": 3},
    EngineerLevel.SENIOR: {"min_avg_score": 85, "min_exp": 150, "min_work_orders": 10},
    EngineerLevel.EXPERT: {"min_avg_score": 90, "min_exp": 300, "min_work_orders": 25},
}

_LEVEL_ORDER = {
    EngineerLevel.JUNIOR: 0,
    EngineerLevel.INTERMEDIATE: 1,
    EngineerLevel.SENIOR: 2,
    EngineerLevel.EXPERT: 3,
}


class EngineerLevelService:
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

    async def check_and_promote(self, user_id: int) -> str:
        """检查并自动晋级，返回新等级或当前等级"""
        async with async_session_factory() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return ""

            current_level = user.工程师等级 or EngineerLevel.JUNIOR
            current_order = _LEVEL_ORDER.get(current_level, 0)

            # 考核均分
            avg_result = await session.execute(
                select(func.avg(ExamRecord.总得分)).where(
                    ExamRecord.用户ID == user_id,
                    ExamRecord.状态 == "completed"
                )
            )
            avg_score = avg_result.scalar() or 0

            # 工单数
            wo_result = await session.execute(
                select(func.count()).select_from(WorkOrder).where(
                    WorkOrder.维修人员ID == user_id,
                    WorkOrder.工单状态 == "completed"
                )
            )
            wo_count = wo_result.scalar() or 0

            exp = user.经验值 or 0

            # 从高到低检查可以晋升到哪一级
            for level, rules in [
                (EngineerLevel.EXPERT, _PROMOTION_RULES[EngineerLevel.EXPERT]),
                (EngineerLevel.SENIOR, _PROMOTION_RULES[EngineerLevel.SENIOR]),
                (EngineerLevel.INTERMEDIATE, _PROMOTION_RULES[EngineerLevel.INTERMEDIATE]),
            ]:
                if _LEVEL_ORDER.get(level, 0) <= current_order:
                    continue
                if (avg_score >= rules["min_avg_score"]
                        and exp >= rules["min_exp"]
                        and wo_count >= rules["min_work_orders"]):
                    user.工程师等级 = level
                    await session.commit()
                    logger.info(f"用户 {user_id} 从 {current_level} 晋级为 {level}")
                    return level

            return current_level

    def get_visible_doc_levels(self, level: str) -> list[str]:
        """根据工程师等级返回可访问的文档等级列表"""
        order = _LEVEL_ORDER.get(level, 0)
        return [
            lv for lv, ord in _LEVEL_ORDER.items() if ord <= order
        ]


engineer_level_service = EngineerLevelService()