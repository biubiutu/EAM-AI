from openai import AsyncOpenAI
from app.config.settings import settings
import json
import base64
import os


IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


class AIClient:
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
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            timeout=120.0,
        )
        self._siliconflow_client = None

    def _get_siliconflow_client(self):
        if self._siliconflow_client is None:
            from app.config.settings import settings as s
            self._siliconflow_client = AsyncOpenAI(
                api_key=s.SILICON_FLOW_API_KEY,
                base_url=s.SILICON_FLOW_BASE_URL,
                timeout=60.0,
            )
        return self._siliconflow_client

    async def chat(self, prompt: str, model: str = None, temperature: float = 0.7) -> str:
        response = await self.client.chat.completions.create(
            model=model or settings.AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def chat_with_json(self, prompt: str, model: str = None) -> dict:
        response = await self.client.chat.completions.create(
            model=model or settings.AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return json.loads(content)

    @staticmethod
    def get_image_mime_type(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        return IMAGE_MIME_TYPES.get(ext, "image/jpeg")

    async def chat_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> str:
        """使用硅基流动视觉模型识别图片"""
        if not settings.SILICON_FLOW_API_KEY:
            raise ValueError("未配置 SILICON_FLOW_API_KEY，无法调用硅基流动视觉模型")
        return await self._chat_with_image_siliconflow(prompt, image_bytes, mime_type=mime_type)

    async def extract_document_text_from_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> str:
        """从文档/手册图片中提取纯文本（硅基流动 OCR）"""
        prompt = (
            "请完整提取这张维修手册或技术文档图片中的所有文字，"
            "保持原有段落与换行，只输出原文，不要添加任何解释。"
        )
        return await self.chat_with_image(prompt, image_bytes, mime_type=mime_type)

    async def _chat_with_image_siliconflow(
        self, prompt: str, image_bytes: bytes, model: str = None, mime_type: str = "image/jpeg"
    ) -> str:
        """Send an image to SiliconFlow's cloud vision model (fast, GPU-powered)"""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"
        client = self._get_siliconflow_client()
        response = await client.chat.completions.create(
            model=model or settings.SILICON_FLOW_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }],
            temperature=0.3,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    async def chat_stream(self, prompt: str, model: str = None, temperature: float = 0.7):
        """流式聊天，逐 token yield"""
        stream = await self.client.chat.completions.create(
            model=model or settings.AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def chat_stream_with_sources(self, prompt: str, sources: list = None, model: str = None, temperature: float = 0.7):
        """流式聊天，增加sources事件和answer事件"""
        import json
        # 先 yield sources 事件
        if sources:
            yield f"event: sources\ndata: {json.dumps({'引用片段': sources}, ensure_ascii=False)}\n\n"

        # 再 yield answer 事件
        full_answer = ""
        async for text in self.chat_stream(prompt, model=model, temperature=temperature):
            full_answer += text
            yield f"event: chunk\ndata: {json.dumps({'text': full_answer}, ensure_ascii=False)}\n\n"

        # done 事件
        yield f"event: done\ndata: {json.dumps({'text': full_answer}, ensure_ascii=False)}\n\n"


ai_client = AIClient()