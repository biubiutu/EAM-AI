"""
PDF 版面解析器
=================
基于 PyMuPDF 实现 PDF 版面分析，提取：
- 文本块（content, page_num, bbox）
- 图片块（image_bytes, page_num, bbox, 可选的 OCR 描述）
- 阅读顺序

输出结构化 LayoutBlock 列表，供 mixed_chunker 做图文混合切片。

如需替换为 MinerU，只需实现相同的 parse() 接口即可。
"""

import os
import logging
import hashlib
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class LayoutBlock:
    """版面中的一个元素块"""
    block_type: str          # "text" | "image" | "table" | "title"
    content: str             # 文本内容（图片块此处为空，由后期 OCR 填充）
    page_num: int            # 页码（从 0 开始）
    bbox: tuple              # (x0, y0, x1, y1) 坐标
    reading_order: int = 0   # 阅读顺序编号
    image_bytes: Optional[bytes] = None   # 图片二进制（仅 image 块有）
    image_ext: str = ""       # 图片扩展名（仅 image 块有）
    image_hash: str = ""      # 图片内容 hash（用于去重）
    metadata: dict = field(default_factory=dict)  # 额外元数据（如表格结构等）

    @property
    def area(self) -> float:
        return (self.bbox[2] - self.bbox[0]) * (self.bbox[3] - self.bbox[1])


class PdfLayoutParser:
    """PDF 版面解析器（PyMuPDF 实现）"""

    MIN_TEXT_LENGTH = 3       # 文本块最小字符数（过滤过短片段）
    MIN_IMAGE_SIZE = 1024     # 图片最小尺寸（bytes），排除图标/装饰性小图

    # 标题字号阈值（相对于页面平均字号）
    TITLE_SIZE_RATIO = 1.3

    def __init__(self, min_image_size: int = None):
        if min_image_size is not None:
            self.MIN_IMAGE_SIZE = min_image_size

    def parse(self, pdf_path: str) -> list[LayoutBlock]:
        """
        解析 PDF 文件，返回按阅读顺序排列的 LayoutBlock 列表。

        Args:
            pdf_path: PDF 文件路径

        Returns:
            按阅读顺序排列的 LayoutBlock 列表
        """
        import fitz

        doc = fitz.open(pdf_path)
        blocks: list[LayoutBlock] = []
        # 全局阅读顺序计数
        global_order = 0

        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

                # 收集本页所有文本块的字体大小，用于估算标题阈值
                font_sizes = self._collect_font_sizes(page_blocks)
                avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                title_threshold = avg_font_size * self.TITLE_SIZE_RATIO

                # 先提取所有文本块
                text_order = 0
                for block in page_blocks:
                    if block["type"] == 0:  # 文本块
                        text_content = self._extract_text_from_block(block)
                        if not text_content or len(text_content.strip()) < self.MIN_TEXT_LENGTH:
                            continue

                        # 判断是否为标题（字号较大或加粗）
                        block_type = "title" if self._is_title(block, title_threshold) else "text"
                        bbox = tuple(block["bbox"])

                        blocks.append(LayoutBlock(
                            block_type=block_type,
                            content=text_content.strip(),
                            page_num=page_num,
                            bbox=bbox,
                            reading_order=global_order,
                            metadata={"font_sizes": font_sizes} if block_type == "title" else {},
                        ))
                        global_order += 1
                        text_order += 1

                # 提取图片
                images_on_page = page.get_image_info(xrefs=True)
                for img_info in images_on_page:
                    try:
                        image_bytes, ext = self._extract_image(page, img_info)
                        if not image_bytes or len(image_bytes) < self.MIN_IMAGE_SIZE:
                            continue

                        img_hash = hashlib.md5(image_bytes).hexdigest()
                        bbox = tuple(img_info.get("bbox", (0, 0, 0, 0)))

                        blocks.append(LayoutBlock(
                            block_type="image",
                            content="",
                            page_num=page_num,
                            bbox=bbox,
                            reading_order=global_order,
                            image_bytes=image_bytes,
                            image_ext=ext,
                            image_hash=img_hash,
                        ))
                        global_order += 1
                    except Exception as exc:
                        logger.debug("提取图片失败 page=%s: %s", page_num, exc)
                        continue

        finally:
            doc.close()

        # 按 (page_num, reading_order) 排序，确保阅读顺序
        blocks.sort(key=lambda b: (b.page_num, b.reading_order))

        return blocks

    # ----- 内部辅助方法 -----

    def _collect_font_sizes(self, page_blocks: list) -> list[float]:
        """收集页面中所有文本块的字体大小"""
        sizes = []
        for block in page_blocks:
            if block["type"] != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("size", 0) > 0:
                        sizes.append(span["size"])
        return sizes or [12]

    def _extract_text_from_block(self, block: dict) -> str:
        """从 PyMuPDF 文本块字典中提取纯文本"""
        parts = []
        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if line_text.strip():
                parts.append(line_text)
        return "\n".join(parts)

    def _is_title(self, block: dict, title_threshold: float) -> bool:
        """判断文本块是否为标题（字号达到阈值）"""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("size", 0) >= title_threshold:
                    return True
                # 加粗也可能是标题
                if span.get("flags", 0) & 2:  # bold flag
                    return True
        return False

    def _extract_image(self, page, img_info: dict) -> tuple[Optional[bytes], str]:
        """
        从 PDF 页面提取图片内容。
        返回 (image_bytes, extension)
        """
        import fitz

        xref = img_info.get("xref")
        if not xref or xref <= 0:
            return None, ""

        try:
            pix = fitz.Pixmap(page.parent, xref)
            if pix.n < 5:  # RGB 或灰度
                ext = "png"
                img_bytes = pix.tobytes("png")
            else:  # CMYK 等，先转为 RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
                ext = "png"
                img_bytes = pix.tobytes("png")
            return img_bytes, ext
        except Exception:
            # 通过原始流提取
            try:
                stream = page.parent.xref_stream(xref)
                if not stream:
                    return None, ""
                ext = img_info.get("ext", "png") or "png"
                return stream, ext
            except Exception:
                return None, ""


# 全局单例
pdf_layout_parser = PdfLayoutParser()