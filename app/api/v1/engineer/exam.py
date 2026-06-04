from fastapi import Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.exam_service import exam_service


class ExamStartRequest(BaseModel):
    skill_level: dict[str, int]
    exam_type: str = "virtual_fault"


class ExamAnswerRequest(BaseModel):
    exam_context: dict
    user_answer: str
    round_num: int = 1


class ExamHistoryRequest(BaseModel):
    exam_history: list


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
            "/skill-radar",
            response_model=BaseResponse,
            summary="获取技能雷达图",
            description="根据历史考核记录生成技能雷达图数据，展示工程师各项技能水平",
            tags=["工程师-AI考核"],
        )(self.get_skill_radar)

        return self.router

    async def start_exam(self, request: ExamStartRequest, _=Depends(allow_engineer)):
        result = await exam_service.generate_virtual_fault(request.skill_level, request.exam_type)
        return BaseResponse(data=result)

    async def submit_answer(self, request: ExamAnswerRequest, _=Depends(allow_engineer)):
        result = await exam_service.evaluate_answer(
            request.exam_context, request.user_answer, request.round_num
        )
        return BaseResponse(data=result)

    async def get_skill_radar(self, request: ExamHistoryRequest, _=Depends(allow_engineer)):
        result = await exam_service.generate_skill_radar(request.exam_history)
        return BaseResponse(data=result)
