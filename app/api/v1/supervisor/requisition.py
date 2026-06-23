from fastapi import Depends
from pydantic import BaseModel, Field, AliasChoices
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_supervisor
from app.services.ai_services.requisition_agent import requisition_agent


class RequisitionAnalyzeRequest(BaseModel):
    spare_part_id: int | str = Field(default=0, validation_alias=AliasChoices("备件ID", "spare_part_id"))
    requested_quantity: int = Field(default=None, validation_alias=AliasChoices("数量", "requested_quantity", "quantity"))
    quantity: int = None
    requester_id: int = 0
    spare_part_name: str = Field(default="", validation_alias=AliasChoices("备件名称", "spare_part_name"))
    urgency: str = Field(default="normal", validation_alias=AliasChoices("紧急程度", "urgency"))
    work_order_id: int = None
    inventory_data: dict[str, Any] = None
    work_order_history: list = None
    rejection_history: list = None


class RequisitionRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/analyze",
            response_model=BaseResponse,
            summary="申购分析",
            description="AI分析备件申购合理性，综合库存、工单历史、驳回记录等数据给出审批建议",
            tags=["主管-备件申购"],
        )(self.analyze_requisition)

        return self.router

    async def analyze_requisition(self, request: RequisitionAnalyzeRequest, _=Depends(allow_supervisor)):
        result = await requisition_agent.analyze(
            spare_part_id=request.spare_part_id,
            requested_quantity=request.requested_quantity or request.quantity or 1,
            requester_id=request.requester_id,
            work_order_id=request.work_order_id,
            inventory_data=request.inventory_data,
            work_order_history=request.work_order_history,
            rejection_history=request.rejection_history,
        )
        return BaseResponse(data=result)
