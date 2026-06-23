from fastapi import UploadFile, File, Depends
from pydantic import BaseModel

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer
from app.services.ai_services.multimodal_service import multimodal_service
from app.services.ai_services.rag_service import rag_service
from app.utils.minio_client import minio_client
from app.config.settings import settings
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
            description="上传维修语音录音 → MinIO 存储 → 转文字",
            tags=["工程师-维修报告"],
        )(self.speech_to_text)

        self.router.post(
            "/analyze-image",
            response_model=BaseResponse,
            summary="故障图片分析",
            description="上传设备故障图片 → MinIO 存储 → AI分析",
            tags=["工程师-维修报告"],
        )(self.analyze_fault_image)

        self.router.post(
            "/generate-report",
            response_model=BaseResponse,
            summary="生成维修报告",
            description="根据语音文字、图片分析结果和设备信息，自动生成维修报告并存入知识库",
            tags=["工程师-维修报告"],
        )(self.generate_report)

        return self.router

    async def speech_to_text(self, file: UploadFile = File(...), _=Depends(allow_engineer)):
        content = await file.read()

        # 1. 上传语音文件到 MinIO
        minio_result = minio_client.upload_file(
            content, file.filename,
            bucket=settings.KB_BUCKET_NAME,
            prefix="audio/",
        )

        # 2. 存临时文件用于语音识别
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        result = await multimodal_service.speech_to_text(file_path)
        return BaseResponse(data={"text": result, "storage": minio_result})

    async def analyze_fault_image(self, file: UploadFile = File(...), _=Depends(allow_engineer)):
        content = await file.read()

        # 1. 上传图片到 MinIO
        minio_result = minio_client.upload_file(
            content, file.filename,
            bucket=settings.KB_BUCKET_NAME,
            prefix="fault_images/",
        )

        # 2. 存临时文件用于 AI 分析
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        result = await multimodal_service.analyze_fault_image(file_path)
        result["storage"] = minio_result
        return BaseResponse(data=result)

    async def generate_report(self, request: ReportRequest, _=Depends(allow_engineer)):
        result = await multimodal_service.generate_report(
            voice_text=request.voice_text,
            image_analysis=request.image_analysis,
            equipment_id=request.equipment_id,
        )
        # 自动将维修报告保存到知识库（Milvus）
        report_text = ""
        if isinstance(result, dict):
            report_text = result.get("report", result.get("content", str(result)))
        else:
            report_text = str(result)
        if report_text:
            try:
                await rag_service.ingest_text(
                    text=f"【维修报告-{request.equipment_id}】{report_text}",
                    metadata={"source": "maintenance_report", "equipment_id": request.equipment_id}
                )
            except Exception:
                pass  # 知识库保存失败不影响主流程
        return BaseResponse(data=result)