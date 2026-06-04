from fastapi import Depends
from pydantic import BaseModel
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.predictive_service import predictive_service


class PredictiveRequest(BaseModel):
    iot_data: dict[str, Any]


class PredictiveRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/analyze",
            response_model=BaseResponse,
            summary="预测性维护分析",
            description="分析IoT设备传感器数据，预测设备故障风险和维护时机",
            tags=["工程师-预测性维护"],
        )(self.analyze)

        return self.router

    async def analyze(self, request: PredictiveRequest, _=Depends(allow_engineer)):
        result = await predictive_service.translate_prediction(request.iot_data)
        return BaseResponse(data=result)
