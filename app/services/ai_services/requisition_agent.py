from app.utils.ai_client import ai_client


class RequisitionAgent:
    async def analyze(
        self, spare_part_id: int, requested_quantity: int, requester_id: int,
        work_order_id: int = None, inventory_data: dict = None,
        work_order_history: list = None, rejection_history: list = None,
    ) -> dict:
        prompt = f"""你是备件申购审核专家。请分析以下申购请求。

【申请信息】
- 备件ID: {spare_part_id}
- 申请数量: {requested_quantity}
- 申请人: {requester_id}
- 关联工单: {work_order_id}

【库存现状】
{inventory_data or "暂无库存数据"}

【近期工单与停机事件】
{work_order_history or "暂无相关记录"}

【同类申购驳回历史】
{rejection_history or "暂无驳回记录"}

请以JSON格式输出分析结果：
{{
    "recommended_quantity": {{
        "min": 2,
        "max": 4,
        "reason": "预计至下次到货窗口15天+安全缓冲7天，建议2-4个"
    }},
    "conflict_evidence": [
        "库位A有5个，但其中3个属于预留，可用仅2个",
        "建议先解预留或走调拨"
    ],
    "ai_review_status": "force_review",
    "transfer_suggestion": {{
        "available": true,
        "from_warehouse": "B车间仓库",
        "quantity": 3,
        "reason": "B车间同款备件闲置，可调拨"
    }},
    "risk_analysis": "如果不申购可能导致的后果",
    "cost_analysis": "申购成本 vs 停机损失对比"
}}"""

        return await ai_client.chat_with_json(prompt)


requisition_agent = RequisitionAgent()