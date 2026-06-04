from fastapi import Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_supervisor
from app.services.ai_services.bom_agent import bom_agent


class BOMCheckRequest(BaseModel):
    equipment_id: int
    bom_items: list
    repair_records: list


class EquipmentRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/check-bom",
            response_model=BaseResponse,
            summary="BOM一致性检查",
            description="检查设备BOM清单与维修记录的一致性，识别缺失或异常备件",
            tags=["主管-台账与BOM"],
        )(self.check_bom)

        return self.router

    async def check_bom(self, request: BOMCheckRequest, _=Depends(allow_supervisor)):
        result = await bom_agent.check_bom_consistency(
            request.bom_items, request.repair_records
        )
        return BaseResponse(data=result)
