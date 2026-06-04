from app.utils.ai_client import ai_client


class SourcingAgent:
    async def recommend_suppliers(self, spare_part_spec: str, suppliers: list = None) -> dict:
        prompt = f"""你是采购寻源专家。请根据备件规格书推荐最优供应商。

【备件规格书】
{spare_part_spec}

【合格供应商库】
{suppliers or "暂无合格供应商数据，请基于行业经验推荐"}

请从以下维度综合评估：
1. 品类匹配度
2. 价格竞争力
3. 交付能力
4. 质量表现
5. 服务评价

以JSON格式输出：
{{
    "recommendations": [
        {{
            "supplier_id": 5,
            "supplier_name": "XX轴承有限公司",
            "match_score": 92,
            "reason": "专精轴承品类，历史交付准时率98%，质量合格率99.2%",
            "estimated_price": 42.00,
            "estimated_delivery_days": 5,
            "advantages": ["价格优势", "交期快", "质量稳定"],
            "disadvantages": ["最小起订量较高"],
            "dimension_scores": {{
                "category_match": 95,
                "price": 88,
                "delivery": 92,
                "quality": 99,
                "service": 85
            }}
        }}
    ],
    "search_suggestions": ["建议在1688搜索相关关键词获取更多供应商"]
}}"""

        return await ai_client.chat_with_json(prompt)


sourcing_agent = SourcingAgent()