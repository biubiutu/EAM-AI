from app.utils.ai_client import ai_client
import os


class MultimodalService:
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
        self._whisper_model = None

    def _load_whisper(self):
        if self._whisper_model is None:
            try:
                import whisper
                from app.config.settings import settings
                self._whisper_model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
            except ImportError:
                raise ImportError("openai-whisper 未安装，请执行: pip install openai-whisper")

    async def speech_to_text(self, audio_file_path: str) -> str:
        self._load_whisper()
        result = self._whisper_model.transcribe(audio_file_path, language="zh")
        return result["text"]

    async def analyze_fault_image(self, image_path: str) -> dict:
        prompt = """请识别这张设备故障照片，分析以下内容：

1. 设备类型和故障部位
2. 故障现象描述
3. 可能的原因分析
4. 建议处理措施
5. 安全隐患提示

请以JSON格式输出：
{
    "equipment_type": "设备类型",
    "fault_location": "故障部位",
    "fault_phenomenon": "故障现象",
    "possible_causes": ["原因1", "原因2"],
    "suggested_actions": ["措施1", "措施2"],
    "safety_warnings": ["安全提示"],
    "severity": "low/medium/high/critical"
}"""

        result = await ai_client.chat_with_json(prompt)
        return result

    async def generate_report(
        self, voice_text: str = "", image_analysis: str = "", equipment_id: str = ""
    ) -> dict:
        prompt = f"""根据以下信息生成结构化维修报告。

【设备编号】{equipment_id}

【维修人员口述】{voice_text if voice_text else "无"}

【故障图片分析】{image_analysis if image_analysis else "无"}

请以JSON格式输出维修报告：
{{
    "equipment_id": "设备编号",
    "fault_phenomenon": "故障现象描述",
    "fault_cause": "故障原因分析",
    "action_taken": "处理措施",
    "parts_replaced": ["更换备件列表"],
    "time_spent": "预计耗时(分钟)",
    "difficulty": "easy/medium/hard",
    "follow_up_suggestions": ["后续建议"]
}}"""

        return await ai_client.chat_with_json(prompt)


multimodal_service = MultimodalService()