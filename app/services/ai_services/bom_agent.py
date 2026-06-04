from app.utils.ai_client import ai_client


class BOMAgent:
    async def check_bom_consistency(self, bom_items: list, repair_records: list) -> dict:
        prompt = f"""你是设备资产管理员。请比对BOM与实际维修记录，检查账实不符。

【当前BOM】
{bom_items}

【历史维修更换记录】
{repair_records}

请识别并输出JSON：
{{
    "suspected_items": [
        {{
            "bom_part_id": 1,
            "bom_model": "BOM中记录的型号",
            "actual_model": "实际使用的型号",
            "confidence": 0.85,
            "evidence": [
                {{
                    "type": "work_order_text",
                    "content": "工单文本证据"
                }},
                {{
                    "type": "photo_ocr",
                    "content": "照片OCR识别证据"
                }}
            ],
            "action": "suggest_update"
        }}
    ],
    "summary": "整体BOM健康度评估",
    "suggestions": ["建议1", "建议2"]
}}"""

        return await ai_client.chat_with_json(prompt)


bom_agent = BOMAgent()