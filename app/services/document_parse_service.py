"""
文档解析服务 / Document Parse Service (Phase 7)
===============================================
增强提取 + 结构切片 + 预览确认
"""
import os
import json
import logging
import tempfile
from typing import Optional

from app.utils.ai_client import ai_client
from app.utils.structure_chunker import structure_chunker
from app.utils.pdf_layout_parser import pdf_layout_parser

logger = logging.getLogger(__name__)


class DocumentParseService:
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

    async def parse(self, file_path: str) -> dict:
        """
        解析文档：
        1. 增强提取（文本层 + OCR + 版面分析）
        2. 结构切片
        3. 返回预览数据
        """
        ext = os.path.splitext(file_path)[1].lower()
        raw_text = await self._enhanced_extract(file_path, ext)
        if not raw_text.strip():
            return {"status": "error", "message": "未能提取到文本"}

        # 结构切片
        blocks = pdf_layout_parser.extract_blocks(file_path) if ext == ".pdf" else []
        if blocks:
            chunks = structure_chunker.chunk_blocks(blocks)
        else:
            chunks = structure_chunker.chunk(raw_text, source=os.path.basename(file_path))

        # 提取元数据
        metadata = await self._extract_metadata(raw_text)

        return {
            "status": "ok",
            "metadata": metadata,
            "chunks": chunks,
            "total_chars": len(raw_text),
            "total_chunks": len(chunks),
        }

    async def _enhanced_extract(self, file_path: str, ext: str) -> str:
        """增强提取：文本层 + OCR 结合"""
        from app.services.ai_services.rag_service import RAGService
        rag = RAGService()

        if ext == ".pdf":
            # 尝试文本层提取
            text = rag._extract_pdf_text_layer(file_path)
            if text.strip():
                logger.info("PDF 文本层提取成功: %s chars", len(text))
                return text

            # 文本层为空，使用版面对话框增强 OCR
            logger.info("PDF 文本层为空，使用版面分析 + OCR: %s", os.path.basename(file_path))
            try:
                blocks = pdf_layout_parser.extract_blocks(file_path)
                text_parts = [b["text"] for b in blocks if b.get("text", "").strip()]
                if text_parts:
                    return "\n\n".join(text_parts)
            except Exception as e:
                logger.warning("版面分析失败: %s", e)

            # 最后的兜底：逐页 OCR
            return await rag._extract_pdf_via_vision(file_path)

        return await rag._extract_text(file_path)

    async def _extract_metadata(self, text: str) -> dict:
        """AI 抽取文档元数据"""
        prompt = f"""请从以下文本中提取文档元数据，返回 JSON 格式：
{{
  "title": "文档标题",
  "equipment": ["相关设备名称"],
  "keywords": ["关键词"],
  "summary": "摘要（50字以内）"
}}

文本：
{text[:3000]}
"""
        try:
            result = await ai_client.chat_with_json(prompt)
            return result
        except Exception as e:
            logger.warning("元数据提取失败: %s", e)
            return {"title": "", "equipment": [], "keywords": [], "summary": ""}


document_parse_service = DocumentParseService()