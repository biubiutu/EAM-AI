"""
考试评价服务
"""
import json
import logging
from app.utils.ai_client import ai_client
from app.core.database import async_session_factory
from app.models.user import ExamRecord, User
from app.services.engineer_level_service import engineer_level_service

logger = logging.getLogger(__name__)


class ExamService:
    async def generate_virtual_fault(self, skill_level: dict, exam_type: str = "virtual_fault") -> dict:
        prompt = f"""你是设备维修考核考官。请根据学员技能水平生成一个虚拟故障场景。

【学员技能水平】
{skill_level}

【考核类型】{exam_type}

要求：
1. 故障难度适中，针对薄弱技能重点考察（得分低的维度权重更高）
2. 描述故障现象，但不直接给出原因
3. 引导学员逐步排查

以JSON格式输出：
{{
    "scenario": "故障场景描述",
    "equipment": "设备名称",
    "initial_clues": ["初始线索1", "初始线索2"],
    "questions": [
        {{
            "round": 1,
            "question": "第一轮问题",
            "expected_answer": "期望答案",
            "score": 25
        }}
    ],
    "total_rounds": 4,
    "total_score": 100
}}"""

        return await ai_client.chat_with_json(prompt)

    async def evaluate_answer(self, exam_context: dict, user_answer: str, round_num: int) -> dict:
        prompt = f"""你是维修考核考官。请评估学员的回答。

【考核背景】
{exam_context}

【第{round_num}轮 - 学员回答】
{user_answer}

请评估并输出JSON：
{{
    "score": 85,
    "is_correct": true,
    "correct_answer": "标准答案",
    "missing_points": ["遗漏的关键步骤"],
    "feedback": "改进建议",
    "next_question": "下一轮问题（如果是最后一轮则为null）",
    "exam_completed": false
}}"""

        return await ai_client.chat_with_json(prompt)

    async def generate_skill_radar(self, exam_history: list) -> dict:
        prompt = f"""你是设备维修技能评估专家。请根据历史考核数据生成技能雷达图。

【历史考核记录】
{exam_history}

以JSON格式输出各维度评分（0-100）：
{{
    "电气": 75,
    "机械": 82,
    "液压": 60,
    "PLC": 88,
    "安全规范": 90,
    "综合评分": 79,
    "等级": "中级",
    "优势维度": ["PLC", "安全规范"],
    "薄弱维度": ["液压"],
    "培训建议": "建议加强液压系统知识学习"
}}"""

        return await ai_client.chat_with_json(prompt)

    async def persist_exam(self, user_id: int, exam_type: str, scene: str,
                            total_score: int, detail: list) -> int:
        """将考核结果写入数据库"""
        async with async_session_factory() as session:
            record = ExamRecord(
                用户ID=user_id,
                考核类型=exam_type,
                考核场景=scene,
                总得分=total_score,
                考核详情=json.dumps(detail, ensure_ascii=False),
                状态="completed",
            )
            session.add(record)

            # 更新经验值
            user_result = await session.execute(
                sqlalchemy.select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user.经验值 = (user.经验值 or 0) + total_score

            await session.commit()

            # 自动晋级检查
            try:
                new_level = await engineer_level_service.check_and_promote(user_id)
                if new_level:
                    logger.info(f"用户 {user_id} 考核后晋级为 {new_level}")
            except Exception as e:
                logger.warning("晋级检查失败: %s", e)

            return record.id

    async def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        from sqlalchemy import select, desc
        async with async_session_factory() as session:
            result = await session.execute(
                select(ExamRecord).where(ExamRecord.用户ID == user_id)
                .order_by(desc(ExamRecord.id)).limit(limit)
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


import sqlalchemy
exam_service = ExamService()