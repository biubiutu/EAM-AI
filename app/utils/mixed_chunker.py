"""
图文混合切片器 (Mixed Chunker)
================================
接收 PdfLayoutParser 输出的 LayoutBlock 列表，执行：

1. 图文绑定：将图片与周围的标题、正文段落绑定为一个混合 Chunk
2. 图片语义提取：调用硅基流动 Vision 模型对图片进行 OCR/描述
3. Chunk 拼接：生成 [图标题] + [图OCR/描述] + [正文] 的完整文本
4. 元数据封装：携带 image_path、page_num、bbox 等信息

输出：MixedChunk 列表 → 供 RAGService 向量化后存入 Milvus
"""

import os
import logging
import tempfile
from dataclasses import dataclass, field
from typing import Optional

from app.utils.pdf_layout_parser import LayoutBlock
from app.utils.ai_client import ai_client
from app.utils.minio_client import minio_client
from app.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class MixedChunk:
    """一个图文混合 Chunk"""
    text: str                            # 拼接后的完整文本（含图描述 + 正文）
    chunk_type: str                      # "text" | "image_with_text" | "table"
    page_num: int                        # 页码
    bbox: str                            # 坐标 JSON 字符串
    source: str                          # 来源文件名
    image_path: str = ""                 # MinIO 图片路径（纯文本块为空）
    image_hash: str = ""                 # 图片去重 hash


class MixedChunker:
    """图文混合切片器"""

    # 图片前后关联的最大文本块数
    MAX_CAPTION_BEFORE = 1     # 图前最多取 1 个块（通常是标题/图题）
    MAX_CAPTION_AFTER = 2      # 图后最多取 2 个块（通常是解释正文）
    # 图片与文本的最大垂直距离（磅），超过则不算关联
    MAX_VERTICAL_GAP = 150
    # 图片描述提示词
    IMAGE_DESCRIBE_PROMPT = (
        "请详细描述这张图片中的所有内容。如果是技术图表、示意图或设备照片，"
        "请提取图中所有可见的文字标注，并描述图示内容。"
        "如果是流程图或结构图，请说明各个组成部分及其关系。"
    )

    def __init__(self, source: str = ""):
        self.source = source

    def chunk(self, blocks: list[LayoutBlock]) -> list[MixedChunk]:
        """
        将 LayoutBlock 列表处理为 MixedChunk 列表。

        策略：
        - 纯文本块：连续文本合并为一个 Chunk（控制总长度）
        - 图片块：向前/后扫描关联文本块，绑定为一个 image_with_text Chunk
        - 过程中对图片调用 Vision API 提取描述文本
        """
        if not blocks:
            return []

        chunks: list[MixedChunk] = []
        i = 0
        while i < len(blocks):
            block = blocks[i]

            if block.block_type == "image":
                # 图片 → 执行图文绑定
                chunk = self._build_image_chunk(blocks, i)
                chunks.append(chunk)
                # 跳过已绑定的文本块
                skip = 1 + chunk.metadata.get("consumed_ahead", 0) + chunk.metadata.get("consumed_behind", 0)
                i += skip
            else:
                # 文本块 → 合并连续的文本
                chunk = self._build_text_chunk(blocks, i)
                chunks.append(chunk)
                i += chunk.metadata.get("consumed", 1)

        # 清理 metadata（不需要传递到外部）
        for chunk in chunks:
            chunk.metadata = {}

        return chunks

    # ----- 图片 Chunk 构建 -----

    def _build_image_chunk(self, blocks: list[LayoutBlock], idx: int) -> MixedChunk:
        """构建一个图文混合 Chunk：绑定图片 + 前后文"""
        img_block = blocks[idx]

        # 1. 扫描图前的文本块（标题/图题）
        ahead_blocks: list[LayoutBlock] = []
        for j in range(idx - 1, max(idx - 1 - self.MAX_CAPTION_BEFORE, -1), -1):
            prev = blocks[j]
            if prev.block_type in ("text", "title") and self._is_vertically_near(prev, img_block):
                ahead_blocks.insert(0, prev)
            else:
                break

        # 2. 扫描图后的文本块（解释正文）
        behind_blocks: list[LayoutBlock] = []
        for j in range(idx + 1, min(idx + 1 + self.MAX_CAPTION_AFTER, len(blocks))):
            nxt = blocks[j]
            if nxt.block_type == "image":
                break  # 遇到下一张图就停止
            if nxt.block_type in ("text", "title") and self._is_vertically_near(nxt, img_block):
                behind_blocks.append(nxt)
            else:
                break

        # 3. 图片 OCR/描述（硅基流动 Vision API）
        image_description = self._describe_image(img_block)

        # 4. 上传图片到 MinIO
        image_path = self._upload_image(img_block)

        # 5. 拼接文本
        parts = []
        for ab in ahead_blocks:
            if ab.block_type == "title":
                parts.append(f"【{ab.content}】")
            else:
                parts.append(ab.content)

        if image_description:
            parts.append(f"[图片描述: {image_description}]")

        for bb in behind_blocks:
            parts.append(bb.content)

        text = "\n".join(parts)

        # 6. 构建 Chunk
        chunk = MixedChunk(
            text=text,
            chunk_type="image_with_text",
            page_num=img_block.page_num,
            bbox=f'{{"x0":{img_block.bbox[0]}, "y0":{img_block.bbox[1]}, '
                 f'"x1":{img_block.bbox[2]}, "y1":{img_block.bbox[3]}}}',
            source=self.source,
            image_path=image_path,
            image_hash=img_block.image_hash,
        )
        chunk.metadata = {
            "consumed_ahead": len(ahead_blocks),
            "consumed_behind": len(behind_blocks),
        }
        return chunk

    def _is_vertically_near(self, text_block: LayoutBlock, img_block: LayoutBlock) -> bool:
        """判断文本块和图片块是否在垂直方向上接近（同页且间距小）"""
        if text_block.page_num != img_block.page_num:
            return False
        # 计算垂直间距
        if text_block.bbox[1] < img_block.bbox[3]:  # 文本在图片上方
            gap = img_block.bbox[1] - text_block.bbox[3]
        else:  # 文本在图片下方
            gap = text_block.bbox[1] - img_block.bbox[3]
        return gap < self.MAX_VERTICAL_GAP

    def _describe_image(self, img_block: LayoutBlock) -> str:
        """调用硅基流动 Vision 模型获取图片描述/OCR 文本"""
        if not img_block.image_bytes:
            return ""
        try:
            mime_type = ai_client.get_image_mime_type(f"img.{img_block.image_ext}")
            text = ai_client.chat_with_image(
                prompt=self.IMAGE_DESCRIBE_PROMPT,
                image_bytes=img_block.image_bytes,
                mime_type=mime_type,
            )
            return text.strip() if text and text.strip() else ""
        except Exception as exc:
            logger.warning("图片描述失败 (page=%s): %s", img_block.page_num, exc)
            return ""

    def _upload_image(self, img_block: LayoutBlock) -> str:
        """将图片上传到 MinIO，返回 MinIO 路径"""
        if not img_block.image_bytes:
            return ""
        try:
            filename = f"pdf_img_{img_block.image_hash or 'unknown'}.{img_block.image_ext or 'png'}"
            prefix = f"knowledge-images/pdf/{self.source.replace('/', '_')}/"
            result = minio_client.upload_file(
                img_block.image_bytes,
                filename,
                bucket=settings.KB_BUCKET_NAME,
                prefix=prefix,
            )
            # result 可能是 dict 包含 file_path
            if isinstance(result, dict):
                return result.get("file_path", f"{prefix}{filename}")
            return f"{prefix}{filename}"
        except Exception as exc:
            logger.error("上传图片到 MinIO 失败: %s", exc)
            return ""

    # ----- 文本 Chunk 构建 -----

    def _build_text_chunk(self, blocks: list[LayoutBlock], start_idx: int) -> MixedChunk:
        """合并连续文本块为一个 Chunk（控制最大长度）"""
        parts = []
        bbox = blocks[start_idx].bbox
        page_num = blocks[start_idx].page_num
        consumed = 0

        for j in range(start_idx, len(blocks)):
            blk = blocks[j]
            if blk.block_type == "image":
                break  # 遇到图片停止
            if blk.block_type in ("text", "title"):
                prefix = "【" + blk.content + "】" if blk.block_type == "title" else blk.content
                parts.append(prefix)
                consumed += 1
                # 更新 bbox 范围
                bbox = (
                    min(bbox[0], blk.bbox[0]),
                    min(bbox[1], blk.bbox[1]),
                    max(bbox[2], blk.bbox[2]),
                    max(bbox[3], blk.bbox[3]),
                )
            else:
                break

        text = "\n".join(parts)
        chunk_type = "title_block" if blocks[start_idx].block_type == "title" else "text"

        chunk = MixedChunk(
            text=text,
            chunk_type=chunk_type,
            page_num=page_num,
            bbox=f'{{"x0":{bbox[0]}, "y0":{bbox[1]}, '
                 f'"x1":{bbox[2]}, "y1":{bbox[3]}}}',
            source=self.source,
        )
        chunk.metadata = {"consumed": consumed}
        return chunk


# 便捷函数
def create_mixed_chunks(blocks: list[LayoutBlock], source: str = "") -> list[MixedChunk]:
    chunker = MixedChunker(source=source)
    return chunker.chunk(blocks)