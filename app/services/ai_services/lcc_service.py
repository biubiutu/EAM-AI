from app.utils.ai_client import ai_client


class LCCService:
    async def analyze_lcc(self, equipment: dict, cost_data: dict) -> dict:
        prompt = f"""你是设备全生命周期成本分析专家。请分析以下设备。

【设备信息】
{equipment}

【成本数据】
采购成本: {cost_data.get('purchase_cost', 0)}
累计维修人工: {cost_data.get('total_repair_labor', 0)}
累计备件消耗: {cost_data.get('total_parts_cost', 0)}
累计停机损失: {cost_data.get('total_downtime_loss', 0)}

请以JSON格式输出：
{{
    "lcc_total": 500000.00,
    "lcc_breakdown": {{
        "purchase_cost": 200000,
        "repair_labor": 150000,
        "parts_cost": 100000,
        "downtime_loss": 50000
    }},
    "health_score": 65,
    "recommendation": "replace",
    "reason": "A设备虽新但维修费高，年均维修成本已超采购成本30%，建议淘汰",
    "comparison": "与同类设备相比，维修成本高20%",
    "roi_analysis": "如果更换新设备，预计2年回本"
}}"""

        return await ai_client.chat_with_json(prompt)


lcc_service = LCCService()