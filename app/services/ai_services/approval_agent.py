from app.utils.ai_client import ai_client


class ApprovalAgent:
    async def generate_summary(self, business_type: str, business_data: dict) -> dict:
        prompt = f"""你是审批决策助手。请为领导生成审批摘要。

【业务类型】{business_type}

【业务数据】
{business_data}

请以JSON格式输出：
{{
    "summary": "本次采购金额超预算10%（+5000元），但供应商A交期最快（3天），且历史履约评分95分。综合考虑停机损失（2000元/天），建议批准。",
    "recommendation": "approve",
    "key_points": [
        "关键要点1",
        "关键要点2"
    ],
    "risk_analysis": "风险分析",
    "budget_analysis": "预算分析",
    "alternative_if_reject": "如果驳回，替代方案是什么"
}}"""

        return await ai_client.chat_with_json(prompt)


approval_agent = ApprovalAgent()