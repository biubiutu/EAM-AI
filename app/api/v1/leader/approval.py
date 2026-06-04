from fastapi import Depends
from pydantic import BaseModel
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_leader
from app.services.ai_services.approval_agent import approval_agent


class ApprovalReviewRequest(BaseModel):
    business_type: str
    business_data: dict[str, Any]


class ApprovalRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/review",
            response_model=BaseResponse,
            summary="审批决策辅助",
            description="AI分析业务数据，生成审批建议和风险提示，辅助领导决策",
            tags=["领导-审批决策"],
        )(self.review_approval)

        return self.router

    async def review_approval(self, request: ApprovalReviewRequest, _=Depends(allow_leader)):
        result = await approval_agent.generate_summary(
            request.business_type, request.business_data
        )
        return BaseResponse(data=result)
