from fastapi import UploadFile, File, Depends
from pydantic import BaseModel, Field

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer, get_current_user
from app.services.ai_services.rag_service import rag_service
from app.services.ai_services.multimodal_service import multimodal_service
from app.services.ai_services.diagnosis_service import diagnosis_service
from app.services.ai_services.predictive_service import predictive_service
from app.services.ai_services.exam_service import exam_service
import aiofiles
import os
import tempfile


class KnowledgeQuery(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=10)


class KnowledgeRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/search",
            response_model=BaseResponse,
            summary="知识问答搜索",
            description="基于向量检索的知识库问答，返回相关知识片段",
            tags=["工程师-知识问答"],
        )(self.search_knowledge)

        self.router.post(
            "/upload-manual",
            response_model=BaseResponse,
            summary="上传维修手册",
            description="上传设备维修手册PDF文件，自动解析并向量化存储",
            tags=["工程师-知识问答"],
        )(self.upload_manual)

        self.router.post(
            "/fault-cases/search",
            response_model=BaseResponse,
            summary="故障案例搜索",
            description="基于向量检索的历史故障案例搜索，返回相似故障及解决方案",
            tags=["工程师-知识问答"],
        )(self.search_fault_cases)

        return self.router

    async def search_knowledge(self, query: KnowledgeQuery, _=Depends(allow_engineer)):
        result = await rag_service.query_knowledge(query.question, query.top_k)
        return BaseResponse(data=result)

    async def upload_manual(self, file: UploadFile = File(...), _=Depends(allow_engineer)):
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        result = await rag_service.ingest_manual(file_path, file.filename)
        return BaseResponse(data={"ingested_chunks": len(result), "source": file.filename})

    async def search_fault_cases(self, query: KnowledgeQuery, _=Depends(allow_engineer)):
        result = await rag_service.search_fault_cases(query.question, query.top_k)
        return BaseResponse(data=result)
