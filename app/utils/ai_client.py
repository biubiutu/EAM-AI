from openai import AsyncOpenAI
from app.config.settings import settings
import json


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


ai_client = AIClient()