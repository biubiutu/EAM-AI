from fastapi import Depends
from pydantic import BaseModel, Field, AliasChoices

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.diagnosis_service import diagnosis_service


class DiagnosisRequest(BaseModel):
    fault_desc: str = Field(..., validation_alias=AliasChoices("故障描述", "fault_desc"))
    equipment_id: int | str | None = Field(default=None, validation_alias=AliasChoices("设备ID", "equipment_id"))
    equipment_model: str = Field(default="", validation_alias=AliasChoices("设备型号", "equipment_model"))
    image_urls: list[str] = []


class DiagnosisRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/diagnose",
            response_model=BaseResponse,
            summary="故障诊断",
            description="根据故障描述和设备信息，AI分析可能的故障原因并提供维修建议",
            tags=["工程师-故障诊断"],
        )(self.diagnose)

        return self.router

    async def diagnose(self, request: DiagnosisRequest, _=Depends(allow_engineer)):
        result = await diagnosis_service.diagnose(
            fault_desc=request.fault_desc,
            equipment_id=request.equipment_id,
            equipment_model=request.equipment_model,
        )
        return BaseResponse(data=result)
