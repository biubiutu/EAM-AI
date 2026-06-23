"""
考核服务 - 工程师等级考核 + 自动晋级
"""
import json
import logging
from sqlalchemy import select, func
from app.core.database import async_session_factory
from app.models.user import ExamRecord, SkillRecord, User
from app.services.engineer_level_service import engineer_level_service
from app.utils.ai_client import ai_client

logger = logging.getLogger(__name__)


class ExamService:
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

    async def generate_exam(self, scene: str = "维修知识", count: int = 10) -> list[dict]:
        """AI 根据场景生成试卷"""
        prompt = f"""你是一位设备维修高级工程师。请根据以下场景生成{count}道技术考核题。

【考核场景】{scene}

要求：
1. 题目包括：单选题、多选题、判断题和简答题
2. 覆盖基础原理、故障排查、安全规范
3. 难度分布：初/中/高/专家级各占约25%
4. 每道题包含：题目、选项（简答题不需要）、正确答案、难度、分值
5. 以JSON数组格式返回：[{{"type": "单选", "question": "...", "options": ["A. ", "B. ", "C. ", "D. "], "answer": "A", "difficulty": "junior", "score": 5}}, ...]
"""
        result = await ai_client.chat_with_json(prompt)
        if isinstance(result, dict) and "questions" in result:
            return result["questions"]
        if isinstance(result, list):
            return result
        return []

    async def submit_exam(self, user_id: int, scene: str, questions: list[dict],
                           answers: list[str]) -> dict:
        """提交考核答案，AI 批卷并写入数据库"""
        # 批卷
        prompt = f"""你是一位严谨的考官。请批阅以下试卷。

【试卷题目】
{json.dumps(questions, ensure_ascii=False)}

【考生答案】
{json.dumps(answers, ensure_ascii=False)}

请逐题判断对错，计算总分（每题分值见题目定义），输出JSON:
{{"scores": [每道题得分], "total": 总分, "comment": "评语"}}
"""
        grading = await ai_client.chat_with_json(prompt)
        total = grading.get("total", 0)
        scores = grading.get("scores", [])

        # 写考核记录
        async with async_session_factory() as session:
            record = ExamRecord(
                用户ID=user_id,
                考核类型="自动考核",
                考核场景=scene,
                总得分=total,
                考核详情=json.dumps({"questions": questions, "answers": answers, "scores": scores}, ensure_ascii=False),
                状态="completed",
            )
            session.add(record)

            # 累积经验值（每得1分=1经验值）
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.经验值 = (user.经验值 or 0) + total

            await session.commit()

            # 检查自动晋级
            new_level = await engineer_level_service.check_and_promote(user_id)

        return {
            "total": total,
            "scores": scores,
            "comment": grading.get("comment", ""),
            "record_id": record.id,
            "new_level": new_level,
        }

    async def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            result = await session.execute(
                select(ExamRecord).where(ExamRecord.用户ID == user_id)
                .order_by(ExamRecord.id.desc()).limit(limit)
            )
            records = result.scalars().all()
            return [{
                "id": r.id,
                "考核类型": r.考核类型,
                "考核场景": r.考核场景,
                "总得分": r.总得分,
                "状态": r.状态,
                "created_at": str(r.created_at),
            } for r in records]


exam_service = ExamService()