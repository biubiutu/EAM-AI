from app.utils.ai_client import ai_client


class ContractAgent:
    async def review_contract(self, contract_text: str, contract_type: str = "purchase") -> dict:
        prompt = f"""你是资深法务专家。请审查以下{contract_type}合同草案，识别潜在风险。

【合同文本】
{contract_text}

请重点检查以下风险类型：
1. 违约金过高/过低
2. 质保期过短
3. 隐形收费条款
4. 严苛罚则
5. 付款条件不对等
6. 知识产权归属不清
7. 争议解决条款不利
8. 不可抗力范围过窄

以JSON格式输出审查结果：
{{
    "risk_level": "medium",
    "overall_score": 75,
    "risks": [
        {{
            "clause_location": "第8条第2款",
            "clause_content": "原文引用",
            "risk_type": "违约金过高",
            "severity": "high",
            "description": "违约金为合同总额30%，远超行业惯例",
            "suggestion": "建议修改为不超过合同总额的10%-15%",
            "legal_basis": "《民法典》第585条"
        }}
    ],
    "positive_clauses": [
        "第15条约定了明确的质量验收标准"
    ],
    "missing_clauses": [
        "缺少保密条款，建议增加",
        "缺少知识产权归属条款"
    ]
}}"""

        return await ai_client.chat_with_json(prompt)


contract_agent = ContractAgent()