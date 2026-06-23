from app.utils.ai_client import ai_client


class Text2SQLService:
    async def generate_sql(self, question: str, table_schema: str = "") -> dict:
        prompt = f"""你是企业数据助手。请直接回答以下业务问题，用自然语言给出清晰、简洁的答案。
如果问题涉及具体数据，请根据你对数据库结构的了解，合理推测数据并给出有参考价值的答案。
不要生成SQL语句，不要输出JSON格式。

【数据库结构】
{table_schema or "eam_ai数据库，包含equipments/work_orders/spare_parts/inventory_records/requisitions/suppliers等表"}

【用户问题】
{question}

请直接回答，以友好的语气提供简明扼要的分析结果。"""

        text = await ai_client.chat(prompt)
        return {"content": text}

    async def generate_insight(self, question: str, query_result: list) -> dict:
        prompt = f"""你是数据分析师。请根据以下查询结果生成洞察。

【用户问题】{question}

【查询结果】
{query_result}

请以JSON格式输出：
{{
    "insight": "核心洞察",
    "data": {query_result},
    "chart_type": "bar",
    "suggestions": ["建议1", "建议2"],
    "anomalies": ["发现的异常"]
}}"""

        return await ai_client.chat_with_json(prompt)


text2sql_service = Text2SQLService()