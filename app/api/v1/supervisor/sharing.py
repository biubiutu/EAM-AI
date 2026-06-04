from fastapi import Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_supervisor
from app.services.ai_services.transfer_agent import transfer_agent


class TransferEvaluateRequest(BaseModel):
    spare_part_id: int
    from_warehouse: dict
    to_warehouse: dict
    quantity: int
    logistics_data: dict = None
    waiting_cost: float = 0


class ScanRequest(BaseModel):
    spare_part_id: int
    need_warehouse_id: int
    quantity: int
    all_inventory: list = None


class SharingRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/evaluate",
            response_model=BaseResponse,
            summary="调拨评估",
            description="评估备件跨厂区调拨的可行性，包括物流成本、等待成本等综合分析",
            tags=["主管-跨厂区共享"],
        )(self.evaluate_transfer)

        self.router.post(
            "/scan",
            response_model=BaseResponse,
            summary="全厂区库存扫描",
            description="扫描全公司范围内备件库存，寻找可用调拨的备件资源",
            tags=["主管-跨厂区共享"],
        )(self.scan_company)

        return self.router

    async def evaluate_transfer(self, request: TransferEvaluateRequest, _=Depends(allow_supervisor)):
        result = await transfer_agent.evaluate_transfer(
            spare_part_id=request.spare_part_id,
            from_warehouse=request.from_warehouse,
            to_warehouse=request.to_warehouse,
            quantity=request.quantity,
            logistics_data=request.logistics_data,
            waiting_cost=request.waiting_cost,
        )
        return BaseResponse(data=result)

    async def scan_company(self, request: ScanRequest, _=Depends(allow_supervisor)):
        result = await transfer_agent.scan_company_wide(
            spare_part_id=request.spare_part_id,
            need_warehouse_id=request.need_warehouse_id,
            quantity=request.quantity,
            all_inventory=request.all_inventory,
        )
        return BaseResponse(data=result)
