from app.utils.ai_client import ai_client


class SupplierRiskAgent:
    async def monitor_supplier_risks(self, supplier: dict) -> list:
        prompt = f"""你是供应链风控专家。请分析以下供应商可能存在的风险。

【供应商信息】
- 名称：{supplier.get('name', '')}
- 地址：{supplier.get('address', '')}
- 主营品类：{supplier.get('categories', [])}

请基于公开信息判断是否存在以下风险，以JSON数组格式输出：
[
    {{
        "alert_type": "news_negative",
        "severity": "warning",
        "title": "风险标题",
        "content": "详细描述",
        "source": "信息来源",
        "ai_suggestion": "建议措施"
    }}
]

如果无风险，返回空数组[]。"""

        result = await ai_client.chat_with_json(prompt)
        return result if isinstance(result, list) else []

    async def assess_risks(self, alerts: list, supplier: dict) -> dict:
        prompt = f"""你是供应链风控总监。请综合评估以下供应商风险。

【供应商信息】
{supplier}

【检测到的风险】
{alerts}

请以JSON格式输出：
{{
    "overall_risk_level": "low/medium/high/critical",
    "should_activate_backup": false,
    "emergency_measures": ["应急措施1", "应急措施2"],
    "monitoring_suggestions": ["监控建议"]
}}"""

        return await ai_client.chat_with_json(prompt)


supplier_risk_agent = SupplierRiskAgent()