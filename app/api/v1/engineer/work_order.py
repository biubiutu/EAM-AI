from fastapi import UploadFile, File, Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.multimodal_service import multimodal_service
import aiofiles
import os
import tempfile


class ReportRequest(BaseModel):
    voice_text: str = ""
    image_analysis: str = ""
    equipment_id: str = ""


class WorkOrderRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/speech-to-text",
            response_model=BaseResponse,
            summary="语音转文字",
            description="将维修语音录音转换为文字，用于维修报告录入",
            tags=["工程师-维修报告"],
        )(self.speech_to_text)

        self.router.post(
            "/analyze-image",
            response_model=BaseResponse,
            summary="故障图片分析",
            description="使用AI分析设备故障图片，识别故障类型和原因",
            tags=["工程师-维修报告"],
        )(self.analyze_fault_image)

        self.router.post(
            "/generate-report",
            response_model=BaseResponse,
            summary="生成维修报告",
            description="根据语音文字、图片分析结果和设备信息，自动生成维修报告",
            tags=["工程师-维修报告"],
        )(self.generate_report)

        return self.router

    async def speech_to_text(self, file: UploadFile = File(...), _=Depends(allow_engineer)):
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        result = await multimodal_service.speech_to_text(file_path)
        return BaseResponse(data={"text": result})

    async def analyze_fault_image(self, file: UploadFile = File(...), _=Depends(allow_engineer)):
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        result = await multimodal_service.analyze_fault_image(file_path)
        return BaseResponse(data=result)

    async def generate_report(self, request: ReportRequest, _=Depends(allow_engineer)):
        result = await multimodal_service.generate_report(
            voice_text=request.voice_text,
            image_analysis=request.image_analysis,
            equipment_id=request.equipment_id,
        )
        return BaseResponse(data=result)
