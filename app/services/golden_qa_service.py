"""
黄金问答库服务
"""
import json
import logging
from sqlalchemy import select, func
from app.core.database import async_session_factory
from app.models.golden_qa import GoldenQA
from app.utils.minio_client import minio_client
from app.config.settings import settings

logger = logging.getLogger(__name__)


class GoldenQAService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    async def add_from_feedback(self, feedback_id: int, question: str, answer: str, sources: str = "",
                                 scene: str = "knowledge", tags: str = "") -> int:
        """从审核通过的评测记录创建黄金问答"""
        async with async_session_factory() as session:
            qa = GoldenQA(
                问题=question,
                标准答案=answer,
                引用来源=sources,
                场景=scene,
                标签=tags,
                来源评测ID=feedback_id,
            )
            session.add(qa)
            await session.commit()
            await session.refresh(qa)
            # 同步到 MinIO
            self._sync_to_minio()
            return qa.id

    async def search(self, query: str, top_k: int = 3, scene: str = "") -> list[dict]:
        """搜索黄金问答（基于关键词匹配，供RAG优先注入）"""
        async with async_session_factory() as session:
            stmt = select(GoldenQA).order_by(GoldenQA.id.desc()).limit(top_k)
            if scene:
                stmt = stmt.where(GoldenQA.场景 == scene)
            result = await session.execute(stmt)
            items = result.scalars().all()

            # 简单的关键词匹配排序（实际可改用向量检索）
            keywords = set(query.lower().split())
            scored = []
            for qa in items:
                text = (qa.问题 + " " + qa.标准答案).lower()
                score = sum(1 for k in keywords if k in text)
                scored.append((score, qa))
            scored.sort(key=lambda x: -x[0])

            return [
                {"id": qa.id, "问题": qa.问题, "标准答案": qa.标准答案,
                 "引用来源": qa.引用来源, "场景": qa.场景, "标签": qa.标签}
                for _, qa in scored[:top_k]
            ]

    async def list_all(self, scene: str = "", page: int = 1, page_size: int = 20) -> dict:
        async with async_session_factory() as session:
            stmt = select(GoldenQA).order_by(GoldenQA.id.desc())
            count_stmt = select(func.count()).select_from(GoldenQA)
            if scene:
                stmt = stmt.where(GoldenQA.场景 == scene)
                count_stmt = count_stmt.where(GoldenQA.场景 == scene)
            total = (await session.execute(count_stmt)).scalar() or 0
            offset = (page - 1) * page_size
            result = await session.execute(stmt.offset(offset).limit(page_size))
            items = result.scalars().all()
            return {
                "items": [{"id": qa.id, "问题": qa.问题, "标准答案": qa.标准答案,
                           "引用来源": qa.引用来源, "场景": qa.场景, "标签": qa.标签} for qa in items],
                "total": total,
            }

    def _sync_to_minio(self):
        """同步黄金问答 JSON 到 MinIO（供 RAG/Vanna 共用）"""
        import asyncio
        try:
            asyncio.create_task(self._async_sync_to_minio())
        except Exception as e:
            logger.warning(f"同步黄金问答到 MinIO 失败: {e}")

    async def _async_sync_to_minio(self):
        try:
            items = (await self.list_all(page=1, page_size=9999))["items"]
            data = json.dumps(items, ensure_ascii=False, indent=2)
            minio_client.upload_file(
                data.encode("utf-8"),
                "golden_qa.json",
                bucket=settings.MILVUS_DEFAULT_COLLECTION or "vanna-training-data",
                prefix="golden-qa/",
            )
        except Exception as e:
            logger.warning(f"同步黄金问答到 MinIO 失败: {e}")


golden_qa_service = GoldenQAService()