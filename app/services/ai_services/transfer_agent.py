from app.utils.ai_client import ai_client


class TransferAgent:
    async def evaluate_transfer(
        self, spare_part_id: int, from_warehouse: dict, to_warehouse: dict,
        quantity: int, logistics_data: dict = None, waiting_cost: float = 0,
    ) -> dict:
        prompt = f"""你是供应链调度专家。请评估以下调拨方案。

【调出方库存】
{from_warehouse}

【调入方库存】
{to_warehouse}

【物流信息】
{logistics_data or "暂无物流数据"}

【缺货停工等待成本】
{waiting_cost}元/天

请综合评估并输出JSON：
{{
    "feasibility_score": 85,
    "transfer_cost": 350.00,
    "waiting_cost_if_not_transfer": 2000.00,
    "net_benefit": 1650.00,
    "from_warehouse_risk": "低（调出方有充足安全缓冲）",
    "transfer_cycle_days": 2,
    "packaging_cost": 50.00,
    "transport_cost": 200.00,
    "quality_inspection_cost": 100.00,
    "recommendation": "建议调拨，净收益1650元，调拨周期2天",
    "alternative_suggestions": [
        "如紧急，可先调拨2个，剩余走采购流程"
    ]
}}"""

        return await ai_client.chat_with_json(prompt)

    async def scan_company_wide(
        self, spare_part_id: int, need_warehouse_id: int, quantity: int,
        all_inventory: list = None,
    ) -> list:
        if not all_inventory:
            return []

        candidates = []
        for inv in all_inventory:
            if inv.get("warehouse_id") == need_warehouse_id:
                continue
            evaluation = await self.evaluate_transfer(
                spare_part_id,
                {"warehouse": inv.get("warehouse_name")},
                {"warehouse": f"需求仓库{need_warehouse_id}"},
                min(quantity, inv.get("surplus_quantity", 0)),
            )
            candidates.append({
                "warehouse": inv,
                "evaluation": evaluation,
            })

        candidates.sort(key=lambda x: x["evaluation"].get("feasibility_score", 0), reverse=True)
        return candidates


transfer_agent = TransferAgent()