from fastapi import Depends
from pydantic import BaseModel
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_leader
from app.services.ai_services.lcc_service import lcc_service


class LCCRequest(BaseModel):
    equipment_id: int | str
    equipment: dict[str, Any] = None
    cost_data: dict[str, Any] = None
    params: dict[str, Any] = None


class LCCRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/analyze",
            response_model=BaseResponse,
            summary="全生命周期成本分析",
            description="分析设备全生命周期成本，包括采购、运维、报废等各阶段成本",
            tags=["领导-全生命周期成本"],
        )(self.analyze_lcc)

        return self.router

    async def analyze_lcc(self, request: LCCRequest, _=Depends(allow_leader)):
        equipment = request.equipment or {"id": request.equipment_id}
        cost_data = request.cost_data or request.params or {}
        result = await lcc_service.analyze_lcc(equipment, cost_data)
        return BaseResponse(data=result)
