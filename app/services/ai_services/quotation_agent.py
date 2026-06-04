from app.utils.ai_client import ai_client


class QuotationAgent:
    async def extract_from_text(self, raw_text: str) -> dict:
        prompt = f"""你是采购数据提取专家。请从以下报价单文本中提取关键信息。

【报价单文本】
{raw_text}

请以JSON格式输出（数组，支持多行报价）：
[
    {{
        "spare_part_name": "备件名称",
        "specification": "规格型号",
        "unit_price": 45.00,
        "quantity": 100,
        "total_price": 4500.00,
        "currency": "CNY",
        "delivery_days": 7,
        "payment_terms": "月结30天",
        "valid_until": "2024-12-31",
        "tax_included": true
    }}
]

注意：
- 价格统一转为数字类型
- 交期转为天数
- 无法提取的字段填null"""

        return await ai_client.chat_with_json(prompt)

    async def compare_quotations(self, quotations: list[dict]) -> dict:
        prompt = f"""你是采购比价专家。请对比以下{len(quotations)}家供应商的报价。

【报价数据】
{quotations}

请从以下维度综合评估：
1. 价格（单价、总价）
2. 交期（天数）
3. 付款条件（账期）
4. 供应商历史表现（准时率、质量合格率）

以JSON格式输出：
{{
    "recommended_supplier_id": 3,
    "reason": "综合评分最高：价格适中(¥42/个)，交期最快(5天)，准时率98%",
    "dimension_scores": {{
        "price": {{"rank": 2, "score": 85, "details": "..."}},
        "delivery": {{"rank": 1, "score": 95, "details": "..."}},
        "payment_terms": {{"rank": 1, "score": 90, "details": "..."}},
        "quality_history": {{"rank": 1, "score": 98, "details": "..."}}
    }},
    "summary_table": [
        {{
            "supplier_id": 1,
            "supplier_name": "供应商A",
            "unit_price": 45.00,
            "delivery_days": 7,
            "payment_terms": "月结30天",
            "total_score": 82
        }}
    ],
    "negotiation_suggestions": [
        "供应商B价格最低但交期较长，可尝试协商缩短至5天",
        "供应商C付款条件最优，可作为备选"
    ]
}}"""

        return await ai_client.chat_with_json(prompt)

    def extract_pdf_text(self, file_path: str) -> str:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def extract_excel_text(self, file_path: str) -> str:
        import pandas as pd
        df = pd.read_excel(file_path)
        return df.to_string()


quotation_agent = QuotationAgent()