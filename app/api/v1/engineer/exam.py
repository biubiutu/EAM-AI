from fastapi import Depends
from pydantic import BaseModel, Field, AliasChoices

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.exam_service import exam_service


class ExamStartRequest(BaseModel):
    skill_level: dict[str, int] = None
    exam_type: str = Field(default="virtual_fault", validation_alias=AliasChoices("考核类型", "exam_type"))


class ExamAnswerRequest(BaseModel):
    exam_context: dict
    user_answer: str
    round_num: int = 1


class ExamHistoryRequest(BaseModel):
    exam_history: list


class ExamSubmitRequest(BaseModel):
    exam_type: str = "virtual_fault"
    answers: list[str] = []


class ExamRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/start",
            response_model=BaseResponse,
            summary="开始考核",
            description="启动虚拟故障考核，根据技能等级生成故障场景",
            tags=["工程师-AI考核"],
        )(self.start_exam)

        self.router.post(
            "/answer",
            response_model=BaseResponse,
            summary="提交考核答案",
            description="提交用户对当前故障场景的处理答案，AI评估正确性",
            tags=["工程师-AI考核"],
        )(self.submit_answer)

        self.router.post(
            "/submit",
            response_model=BaseResponse,
            summary="批量提交考核答案",
            description="提交全部问题的答案，AI评估并给出综合评分",
            tags=["工程师-AI考核"],
        )(self.submit_exam)

        self.router.post(
            "/skill-radar",
            response_model=BaseResponse,
            summary="获取技能雷达图",
            description="根据历史考核记录生成技能雷达图数据，展示工程师各项技能水平",
            tags=["工程师-AI考核"],
        )(self.get_skill_radar)

        return self.router

    async def start_exam(self, request: ExamStartRequest, _=Depends(allow_engineer)):
        skill = request.skill_level or {"电气": 70, "机械": 65, "液压": 60}
        result = await exam_service.generate_virtual_fault(skill, request.exam_type)
        return BaseResponse(data=result)

    async def submit_answer(self, request: ExamAnswerRequest, _=Depends(allow_engineer)):
        result = await exam_service.evaluate_answer(
            request.exam_context, request.user_answer, request.round_num
        )
        return BaseResponse(data=result)

    async def submit_exam(self, request: ExamSubmitRequest, _=Depends(allow_engineer)):
        """批量提交考核答案，AI逐题评分并给出参考答案"""
        total = len(request.answers)
        if total == 0:
            return BaseResponse(data={"score": 0, "total": 0, "detail": [], "feedback": "未提交答案"})

        # 先获取考核题目（含参考答案）
        skill = {"电气": 70, "机械": 65, "液压": 60}
        exam_data = await exam_service.generate_virtual_fault(skill, request.exam_type)
        questions = exam_data.get("questions", [])

        detail = []
        total_score = 0
        for i, ans in enumerate(request.answers):
            q = questions[i] if i < len(questions) else {"question": f"第{i+1}题", "expected_answer": "无特定要求", "score": round(100/max(total,1), 1)}
            # AI评估用户答案
            eval_result = await exam_service.evaluate_answer(
                exam_context=exam_data,
                user_answer=ans,
                round_num=i+1
            )
            score = eval_result.get("score", q.get("score", 0))
            total_score += score
            detail.append({
                "index": i,
                "question": q.get("question", ""),
                "user_answer": ans,
                "reference_answer": eval_result.get("correct_answer", q.get("expected_answer", "")),
                "score": score,
                "feedback": eval_result.get("feedback", ""),
                "missing_points": eval_result.get("missing_points", [])
            })

        avg_score = round(total_score / max(total, 1), 1)
        return BaseResponse(data={
            "score": avg_score,
            "total": total,
            "detail": detail,
            "feedback": f"本次考核共{total}题，综合评分{avg_score}分。" + 
                       (" ".join([d.get("feedback", "") for d in detail[:3]]) if detail else "")
        })

    async def get_skill_radar(self, request: ExamHistoryRequest, _=Depends(allow_engineer)):
        result = await exam_service.generate_skill_radar(request.exam_history)
        return BaseResponse(data=result)
