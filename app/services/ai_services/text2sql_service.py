from app.utils.ai_client import ai_client


class Text2SQLService:
    async def generate_sql(self, question: str, table_schema: str = "") -> dict:
        prompt = f"""你是数据分析专家。请将用户的自然语言问题转化为SQL查询。

【数据库表结构】
{table_schema or "eam_ai数据库，包含equipments/work_orders/spare_parts/inventory_records/requisitions/suppliers等表"}

【用户问题】
{question}

请以JSON格式输出：
{{
    "sql": "SELECT ... FROM ... WHERE ...",
    "explanation": "SQL解释",
    "result_type": "table/chart/number",
    "chart_recommendation": "建议的图表类型: bar/line/pie",
    "data_fields": ["字段1", "字段2"]
}}"""

        return await ai_client.chat_with_json(prompt)

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