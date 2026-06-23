"""
结构感知切片器 (Structure Chunker)
===================================
按标题/页码/表格边界/步骤边界切片，保持语义完整性。
"""
import re
import logging

logger = logging.getLogger(__name__)


class StructureChunker:
    """结构感知切片器"""

    # 中英文标题正则
    TITLE_PATTERNS = [
        re.compile(r'^(第[一二三四五六七八九十百千]+[章节部篇])\s+'),  # 第一章
        re.compile(r'^(\d+\.?)\s+[^\n]{1,50}$', re.MULTILINE),      # 1.
        re.compile(r'^[一二三四五六七八九十百千]+[、.]\s'),           # 一、
        re.compile(r'^步骤[一二三四五六七八九十百千]+\s', re.MULTILINE),  # 步骤一
    ]

    STEP_PATTERNS = [
        re.compile(r'^\d+[\.\)、]'),  # 1.  1)  1、
        re.compile(r'^步骤\s*\d+', re.IGNORECASE),  # 步骤1
        re.compile(r'^[a-z][\.\)]', re.IGNORECASE),  # a.  b)
    ]

    def chunk(self, text: str, source: str = "", page_num: int = 1, max_chunk_size: int = 1000) -> list[dict]:
        """
        结构感知切片，返回 [{text, title, page_num, type}, ...]
        """
        if not text.strip():
            return []

        chunks = []
        lines = text.split('\n')
        current_chunk = ""
        current_title = ""
        current_lines = []

        def flush():
            nonlocal current_chunk, current_title, current_lines
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "title": current_title,
                    "page_num": page_num,
                    "type": "step" if self._is_step_section(current_title or current_chunk) else "text",
                })
            current_chunk = ""
            current_title = ""
            current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_chunk += "\n"
                continue

            # 检查是否为标题行
            is_title = any(p.match(stripped) for p in self.TITLE_PATTERNS)

            if is_title:
                flush()
                current_title = stripped
                current_chunk = stripped + "\n"
            else:
                # 检查是否超出长度限制
                if len(current_chunk) + len(stripped) > max_chunk_size and current_chunk.strip():
                    # 在段落边界裁切
                    if not stripped.startswith(('　', '  ', '\t')):
                        flush()
                current_chunk += stripped + "\n"

        flush()
        return chunks

    def chunk_blocks(self, blocks: list[dict], max_chunk_size: int = 1000) -> list[dict]:
        """对已提取的文本块做结构感知切片"""
        all_chunks = []
        for block in blocks:
            text = block.get("text", "")
            page = block.get("page_num", 1)
            result = self.chunk(text, max_chunk_size=max_chunk_size, page_num=page)
            for r in result:
                r["source"] = block.get("source", "")
                all_chunks.append(r)
        return all_chunks

    def _is_step_section(self, text: str) -> bool:
        return any(p.match(text.strip()) for p in self.STEP_PATTERNS)


structure_chunker = StructureChunker()