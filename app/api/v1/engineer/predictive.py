from fastapi import Depends
from pydantic import BaseModel, Field, AliasChoices
from typing import Any

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.predictive_service import predictive_service


class PredictiveRequest(BaseModel):
    equipment_id: str = Field(default="", validation_alias=AliasChoices("设备ID", "equipment_id"))
    sensor_data: dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("传感器数据", "sensor_data"))
    iot_data: dict[str, Any] = None


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
        data = request.iot_data if request.iot_data else request.sensor_data
        result = await predictive_service.translate_prediction(data)
        return BaseResponse(data=result)
