from app.utils.ai_client import ai_client


class PriceTrendAgent:
    async def analyze_price_trend(
        self, spare_part_id: int, spare_part_name: str = "",
        raw_materials: list = None, commodity_prices: list = None,
    ) -> dict:
        prompt = f"""你是采购价格分析师。请分析备件价格趋势。

【备件信息】
- 备件ID: {spare_part_id}
- 备件名称: {spare_part_name}
- 关联原材料: {raw_materials or "暂无数据"}

【大宗商品实时价格】
{commodity_prices or "暂无数据"}

请分析并输出JSON：
{{
    "raw_material_impact": [
        {{
            "commodity_name": "钢材",
            "current_price": 4200.00,
            "change_percent": -5.2,
            "trend": "down",
            "cost_impact": "备件成本预计下降3-4%",
            "suggestion": "当前钢材降价5%，建议重新议价或锁定长期合同"
        }}
    ],
    "overall_trend": "down",
    "price_forecast_30d": "预计继续下降2-3%",
    "procurement_suggestions": [
        "建议暂缓采购，等待价格进一步回落",
        "可与供应商协商签订价格联动条款",
        "如急需，可先采购小批量，剩余待价格稳定后补采"
    ],
    "negotiation_leverage": "当前原材料降价，议价空间约5-8%"
}}"""

        return await ai_client.chat_with_json(prompt)


price_trend_agent = PriceTrendAgent()