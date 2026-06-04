from app.utils.ai_client import ai_client
from app.services.ai_services.rag_service import rag_service


class DiagnosisService:
    async def diagnose(self, fault_desc: str, equipment_id: int = None, equipment_model: str = "") -> dict:
        similar_cases = await rag_service.search_fault_cases(fault_desc, top_k=5)

        cases_text = ""
        for i, case in enumerate(similar_cases["cases"], 1):
            cases_text += f"案例{i}：故障类型={case['fault_type']}，处理={case['resolution']}\n"

        prompt = f"""你是设备故障诊断专家。请根据故障描述和历史案例进行诊断。

【故障描述】{fault_desc}

【设备型号】{equipment_model}

【历史相似案例】
{cases_text}

请分析并输出JSON：
{{
    "diagnosis": [
        {{
            "possible_cause": "可能原因",
            "probability": 80,
            "evidence": "依据说明",
            "troubleshooting_steps": ["排查步骤1", "排查步骤2"],
            "resolution": "建议解决方案"
        }}
    ],
    "recommended_action": "最推荐的处理方案",
    "estimated_time": "预计维修时间",
    "safety_warnings": ["安全注意事项"]
}}"""

        return await ai_client.chat_with_json(prompt)


diagnosis_service = DiagnosisService()