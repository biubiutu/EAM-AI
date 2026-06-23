from fastapi import UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, AliasChoices
from pydantic.config import ConfigDict

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
from app.core.security import allow_engineer, get_current_user
from app.services.ai_services.rag_service import rag_service
from app.services.ai_services.multimodal_service import multimodal_service
from app.services.ai_services.diagnosis_service import diagnosis_service
from app.services.ai_services.predictive_service import predictive_service
from app.services.ai_services.exam_service import exam_service
from app.utils.minio_client import minio_client
from app.config.settings import settings
import aiofiles
import os
import tempfile
import logging

logger = logging.getLogger(__name__)


class KnowledgeQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    问题: str = Field(..., validation_alias=AliasChoices("问题", "question"))
    返回条数: int = Field(
        default=3, ge=1, le=10, validation_alias=AliasChoices("返回条数", "top_k")
    )


class IngestCaseRequest(BaseModel):
    fault_desc: str = Field(..., validation_alias=AliasChoices("故障描述", "fault_desc"))
    fault_type: str = Field(default="", validation_alias=AliasChoices("故障类型", "fault_type"))
    resolution: str = Field(default="", validation_alias=AliasChoices("解决方案", "resolution"))


class IngestTextRequest(BaseModel):
    text: str
    metadata: dict = {}


class MultimodalQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    问题: str = Field(..., validation_alias=AliasChoices("问题", "question"))
    返回条数: int = Field(
        default=5, ge=1, le=20, validation_alias=AliasChoices("返回条数", "top_k")
    )
    返回图片: bool = Field(
        default=True, validation_alias=AliasChoices("返回图片", "return_images")
    )


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
            "/search-stream",
            summary="知识问答搜索（SSE流式）",
            description="SSE 流式知识问答，包含 sources/chunk/done 事件",
            tags=["工程师-知识问答"],
        )(self.search_knowledge_stream)

        self.router.post(
            "/upload-manual",
            response_model=BaseResponse,
            summary="上传维修手册",
            description="上传设备维修手册（支持多文件），支持 PDF/TXT/DOC/DOCX/PNG/JPG 等，自动解析 → MinIO 存储 → 切片 → 向量化存入 Milvus。表单字段：files（文件列表）、source（可选手册名称前缀）",
            tags=["工程师-知识问答"],
        )(self.upload_manual)

        self.router.post(
            "/fault-cases/search",
            response_model=BaseResponse,
            summary="故障案例搜索",
            description="基于向量检索的历史故障案例搜索，返回相似故障及解决方案",
            tags=["工程师-知识问答"],
        )(self.search_fault_cases)

        self.router.post(
            "/ingest-case",
            response_model=BaseResponse,
            summary="录入故障案例",
            description="手动录入故障案例到知识库，包含故障描述、类型和解决方案",
            tags=["工程师-知识问答"],
        )(self.ingest_case)

        self.router.post(
            "/ingest",
            response_model=BaseResponse,
            summary="录入维修数据到知识库",
            description="维修作业一站式录入：将维修数据文本向量化存入 Milvus 知识库",
            tags=["工程师-知识问答"],
        )(self.ingest_knowledge)

        self.router.post(
            "/upload-attachment",
            response_model=BaseResponse,
            summary="上传维修附件到MinIO",
            description="上传维修附件到 MinIO，表单字段名 files（支持多文件，取首个）",
            tags=["工程师-知识问答"],
        )(self.upload_attachment)

        # === 统一上传（大模型智能判断处理策略）===
        self.router.post(
            "/upload",
            response_model=BaseResponse,
            summary="上传文档（智能策略）",
            description="统一上传入口。支持 PDF/TXT/DOC/DOCX/PNG/JPG 等文件，系统自动判断使用简单文本切片还是多模态图文混合切片策略。表单字段：files（支持多文件）、source（可选来源前缀）",
            tags=["工程师-知识问答"],
        )(self.smart_upload)

        # === 多模态知识搜索 ===
        self.router.post(
            "/multimodal-search",
            response_model=BaseResponse,
            summary="多模态知识搜索（图文召回）",
            description="在多模态知识库中检索，返回文本切片 + 关联图片的 MinIO 预签名 URL，支持图文并茂的回答",
            tags=["工程师-知识问答"],
        )(self.multimodal_search)

        return self.router

    async def search_knowledge(self, query: KnowledgeQuery, _=Depends(allow_engineer)):
        result = await rag_service.query_knowledge(query.问题, query.返回条数)
        return BaseResponse(data={
            "回答": result.get("answer", ""),
            "引用片段": [
                {
                    "来源": item.get("source", ""),
                    "内容": item.get("content", ""),
                    "距离": item.get("distance"),
                }
                for item in result.get("sources", [])
            ],
        })

    async def search_fault_cases(self, query: KnowledgeQuery, _=Depends(allow_engineer)):
        result = await rag_service.search_fault_cases(query.问题, query.返回条数)
        cases = result.get("cases", [])
        return BaseResponse(data={
            "案例列表": [
                {
                    "内容": c.get("content", ""),
                    "故障类型": c.get("fault_type", ""),
                    "解决方案": c.get("resolution", ""),
                    "距离": c.get("distance"),
                }
                for c in cases
            ],
        })

    async def upload_manual(
        self,
        files: list[UploadFile] = File(...),
        source: str = Form(""),
        _=Depends(allow_engineer),
    ):
        """支持单文件或多文件上传，每个文件独立入 MinIO 并向量化"""
        if not files:
            return BaseResponse(code=400, msg="请至少上传一个文件")

        results = []
        for file in files:
            try:
                content = await file.read()
                if not content:
                    raise ValueError("上传文件为空")
                source_name = f"{source}/{file.filename}" if source else file.filename

                minio_result = minio_client.upload_file(
                    content, file.filename,
                    bucket=settings.KB_BUCKET_NAME,
                    prefix="manuals/",
                )

                tmp_dir = tempfile.mkdtemp()
                file_path = os.path.join(tmp_dir, file.filename)
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)

                chunks = await rag_service.ingest_manual(file_path, source_name)
                results.append({
                    "ingested_chunks": len(chunks),
                    "source": source_name,
                    "filename": file.filename,
                    "storage": minio_result,
                })
            except Exception as exc:
                logger.exception("维修手册入库失败: %s", file.filename)
                results.append({
                    "filename": file.filename,
                    "error": str(exc),
                })

        return BaseResponse(data={
            "total_files": len(results),
            "files": results,
        })

    async def ingest_case(self, request: IngestCaseRequest, _=Depends(allow_engineer)):
        text = f"故障类型：{request.fault_type}\n故障描述：{request.fault_desc}\n解决方案：{request.resolution}"
        await rag_service.ingest_text(text, metadata={"source": "engineer_manual", "fault_type": request.fault_type})
        return BaseResponse(data={"message": "故障案例已录入知识库", "fault_type": request.fault_type})

    async def ingest_knowledge(self, request: IngestTextRequest, _=Depends(allow_engineer)):
        metadata = request.metadata or {}
        await rag_service.ingest_text(request.text, metadata=metadata)
        return BaseResponse(data={"message": "维修数据已录入知识库", "metadata": metadata})

    async def upload_attachment(
        self, files: list[UploadFile] = File(...), _=Depends(allow_engineer)
    ):
        if not files:
            return BaseResponse(code=400, msg="请至少上传一个文件")
        file = files[0]
        content = await file.read()
        result = minio_client.upload_file(
            content, file.filename,
            bucket=settings.KB_BUCKET_NAME,
            prefix="maintenance_attachments/",
        )
        return BaseResponse(data={"storage": result, "filename": file.filename})

    # ========== 统一上传（大模型智能判断处理策略） ==========

    async def smart_upload(
        self,
        files: list[UploadFile] = File(...),
        source: str = Form(""),
        _=Depends(allow_engineer),
    ):
        """
        统一上传入口。

        处理流程：
        1. 保存到 MinIO + 临时文件
        2. 提取文件特征（PDF 需检查页数、图片数量、文本预览）
        3. 大模型判断策略：simple_text 或 multimodal_layout
        4. 路由到对应的处理流水线
        5. 返回统一结果
        """
        if not files:
            return BaseResponse(code=400, msg="请至少上传一个文件")

        results = []
        for file in files:
            try:
                content = await file.read()
                if not content:
                    raise ValueError("上传文件为空")

                source_name = f"{source}/{file.filename}" if source else file.filename

                # 1. 存 MinIO
                minio_result = minio_client.upload_file(
                    content, file.filename,
                    bucket=settings.KB_BUCKET_NAME,
                    prefix="manuals/",
                )

                # 2. 写临时文件
                tmp_dir = tempfile.mkdtemp()
                file_path = os.path.join(tmp_dir, file.filename)
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)

                # 3. 提取文件特征 + 大模型判断策略
                strategy = await self._detect_strategy(file_path, file.filename, len(content))
                logger.info("「%s」策略判定结果: %s", file.filename, strategy)

                # 4. 路由到对应流水线
                if strategy == "multimodal_layout":
                    stats = await rag_service.ingest_pdf_multimodal(file_path, source=source_name)
                    results.append({
                        "filename": file.filename,
                        "source": source_name,
                        "strategy": "multimodal_layout（版面分析 + 图文混合切片）",
                        "storage": minio_result,
                        "stats": stats,
                    })
                else:
                    chunks = await rag_service.ingest_manual(file_path, source_name)
                    results.append({
                        "filename": file.filename,
                        "source": source_name,
                        "strategy": "simple_text（文本提取 + 基础切片）",
                        "storage": minio_result,
                        "ingested_chunks": len(chunks),
                    })

            except Exception as exc:
                logger.exception("文件入库失败: %s", file.filename)
                results.append({
                    "filename": file.filename,
                    "error": str(exc),
                })

        return BaseResponse(data={
            "total_files": len(results),
            "files": results,
        })

    async def _detect_strategy(self, file_path: str, filename: str, file_size: int) -> str:
        """
        提取文件特征，交给大模型判断处理策略。

        返回 "simple_text" 或 "multimodal_layout"。
        """
        ext = os.path.splitext(filename)[1].lower()

        # 非 PDF 文件：直接走简单文本
        if ext != ".pdf":
            return "simple_text"

        # PDF 文件：提取特征
        pdf_page_count = 0
        pdf_has_images = False
        text_preview = ""

        try:
            import fitz
            doc = fitz.open(file_path)
            try:
                pdf_page_count = doc.page_count

                # 检查是否有嵌入图片
                for page_num in range(min(pdf_page_count, 5)):  # 检查前 5 页
                    page = doc.load_page(page_num)
                    img_info = page.get_image_info(xrefs=True)
                    if img_info:
                        pdf_has_images = True

                    # 取第一页文本作为预览
                    if not text_preview:
                        text_preview = page.get_text()[:500]

                if not text_preview:
                    # 尝试取前 3 页拼接
                    for page_num in range(min(pdf_page_count, 3)):
                        page = doc.load_page(page_num)
                        text_preview += page.get_text()
                    text_preview = text_preview[:500]

            finally:
                doc.close()
        except Exception as exc:
            logger.warning("PDF 特征提取失败，默认 simple_text: %s", exc)
            return "simple_text"

        # 交给大模型决策
        return await rag_service.decide_upload_strategy(
            filename=filename,
            file_size=file_size,
            pdf_page_count=pdf_page_count,
            pdf_has_images=pdf_has_images,
            text_preview=text_preview,
        )

    # === 旧端点保留，自动转发到统一入口 ===

    async def upload_manual(
        self,
        files: list[UploadFile] = File(...),
        source: str = Form(""),
        _=Depends(allow_engineer),
    ):
        """【保留兼容】自动转发到统一上传入口"""
        return await self.smart_upload(files=files, source=source, _=_)

    # ========== 多模态知识搜索 ==========

    async def multimodal_search(self, query: MultimodalQuery, _=Depends(allow_engineer)):
        """
        多模态知识库检索，返回文本切片 + 图片 URL
        """
        result = await rag_service.query_multimodal(
            question=query.问题,
            top_k=query.返回条数,
            return_images=query.返回图片,
        )
        return BaseResponse(data={
            "回答": result.get("answer", ""),
            "引用片段": [
                {
                    "内容": s.get("content", ""),
                    "来源": s.get("source", ""),
                    "类型": s.get("chunk_type", ""),
                    "页码": s.get("page_num", -1),
                    "坐标": s.get("bbox", ""),
                    "图片路径": s.get("image_path", ""),
                    "距离": s.get("distance", 0),
                }
                for s in result.get("sources", [])
            ],
            "图片列表": [
                {
                    "路径": img.get("image_path", ""),
                    "预签名URL": img.get("presigned_url", ""),
                    "页码": img.get("page_num", -1),
                }
                for img in result.get("images", [])
            ],
        })

    async def search_knowledge_stream(self, query: KnowledgeQuery, _=Depends(allow_engineer)):
        return StreamingResponse(
            rag_service.query_knowledge_stream(query.问题, query.返回条数),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )