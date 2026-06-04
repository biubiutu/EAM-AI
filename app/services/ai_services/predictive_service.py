from app.utils.ai_client import ai_client


class PredictiveService:
    async def translate_prediction(self, iot_data: dict) -> dict:
        prompt = f"""你是预测性维护专家。请将以下IoT传感器数据转化为可理解的维护建议。

【IoT数据】
{iot_data}

请以JSON格式输出：
{{
    "health_status": "设备健康状态概述",
    "predicted_failure": {{
        "component": "预测可能失效的部件",
        "time_window": "预计失效时间窗口（如：14天内）",
        "confidence": 85
    }},
    "human_readable_advice": "将预测结果翻译成人话（如：预测14天内失效，建议下周二更换SKF 6205）",
    "recommended_action": "建议操作",
    "recommended_date": "建议操作日期",
    "recommended_part": {{
        "name": "推荐备件名称",
        "model": "推荐型号",
        "quantity": 1
    }},
    "risk_level": "low/medium/high/critical",
    "impact_if_ignored": "如果不处理可能造成的后果"
}}"""

        return await ai_client.chat_with_json(prompt)


predictive_service = PredictiveService()