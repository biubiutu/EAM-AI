import sys
sys.path.insert(0, 'D:\\EAM-AI')
import asyncio
from sqlalchemy import text, inspect
from app.core.database import engine

# Mapping: old table name -> new table name
TABLE_MAP = {
    "users": "用户",
    "skill_records": "技能记录",
    "exam_records": "考核记录",
    "equipments": "设备",
    "bom_items": "BOM清单",
    "work_orders": "工单",
    "inspection_records": "巡检记录",
    "maintenance_plans": "维护计划",
    "spare_parts": "备件",
    "warehouses": "仓库",
    "inventory_records": "库存记录",
    "requisitions": "申购单",
    "transfer_orders": "调拨单",
    "stagnant_alerts": "呆滞预警",
    "suppliers": "供应商",
    "supplier_categories": "供应商品类",
    "quotations": "报价单",
    "price_comparisons": "比价记录",
    "contracts": "合同",
    "supplier_risk_alerts": "供应商风险预警",
    "commodity_prices": "大宗商品价格",
    "sourcing_recommendations": "寻源推荐",
    "approval_records": "审批记录",
    "cost_analyses": "成本分析",
    "engineer_dispatches": "工程师调派",
}

# Column mapping per table: old_col -> new_col
COLUMN_MAP = {
    "users": {
        "username": "用户名", "password_hash": "密码哈希", "real_name": "真实姓名",
        "email": "邮箱", "phone": "手机号", "role": "角色", "is_active": "是否激活",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "skill_records": {
        "user_id": "用户ID", "skill_dimension": "技能维度", "score": "技能评分",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "exam_records": {
        "user_id": "用户ID", "exam_type": "考核类型", "scenario": "考核场景",
        "total_score": "总得分", "detail": "考核详情", "status": "状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "equipments": {
        "code": "设备编码", "name": "设备名称", "model": "设备型号", "category": "设备分类",
        "factory_code": "所属厂区", "workshop": "所属车间", "line": "所属产线",
        "status": "设备状态", "purchase_date": "采购日期", "warranty_expiry": "质保到期日",
        "manufacturer": "制造商", "supplier_id": "供应商ID",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "bom_items": {
        "equipment_id": "设备ID", "spare_part_id": "备件ID", "quantity": "标准用量",
        "is_critical": "是否关键备件", "position": "安装位置", "ai_confidence": "AI置信度",
        "ai_evidence": "AI证据来源", "is_suspected_outdated": "是否疑似过时",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "work_orders": {
        "order_no": "工单号", "equipment_id": "设备ID", "fault_phenomenon": "故障现象",
        "fault_cause": "故障原因", "fault_cause_confidence": "AI诊断置信度",
        "action_taken": "处理措施", "parts_replaced": "更换备件列表",
        "time_spent": "耗时分钟", "voice_text": "语音转译文本",
        "photo_urls": "故障照片URL列表", "report_content": "AI维修报告",
        "status": "工单状态", "repairer_id": "维修人员ID", "created_by": "创建人ID",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "inspection_records": {
        "equipment_id": "设备ID", "inspector_id": "巡检人员ID", "inspection_route": "巡检路线",
        "nfc_tag": "NFC标签", "is_normal": "是否正常", "abnormal_desc": "异常描述",
        "abnormal_photo_url": "异常照片", "linked_work_order_id": "关联工单ID",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "maintenance_plans": {
        "equipment_id": "设备ID", "plan_type": "计划类型", "predicted_failure_time": "预测失效时间",
        "ai_prediction": "AI预测描述", "ai_recommendation": "AI建议措施",
        "recommended_part": "建议更换备件", "status": "计划状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "spare_parts": {
        "sku_code": "SKU编码", "name": "备件名称", "specification": "规格型号",
        "category": "分类", "unit": "单位", "unit_price": "参考单价",
        "shelf_life_days": "保质期天数", "min_stock": "最小库存",
        "max_stock": "最大库存", "safety_stock": "安全库存",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "warehouses": {
        "code": "仓库编码", "name": "仓库名称", "factory_code": "所属厂区",
        "address": "地址", "manager_id": "负责人ID",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "inventory_records": {
        "spare_part_id": "备件ID", "warehouse_id": "仓库ID", "location_code": "库位编码",
        "quantity": "账面数量", "available_quantity": "可用数量",
        "reserved_quantity": "预留数量", "reserved_for": "预留用途",
        "batch_no": "批次号", "production_date": "生产日期", "expiry_date": "过期日期",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "requisitions": {
        "requisition_no": "申购单号", "spare_part_id": "备件ID", "requester_id": "申请人ID",
        "requested_quantity": "申请数量", "ai_recommended_quantity": "AI推荐数量",
        "ai_recommended_reason": "AI推荐理由", "ai_review_status": "AI审核状态",
        "ai_review_detail": "AI审核详情", "deviation_reason": "偏离原因",
        "deviation_note": "偏离补充说明", "work_order_id": "关联工单ID", "status": "申购状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "transfer_orders": {
        "transfer_no": "调拨单号", "spare_part_id": "备件ID", "from_warehouse_id": "调出仓库ID",
        "to_warehouse_id": "调入仓库ID", "quantity": "调拨数量",
        "ai_feasibility_score": "AI可行性打分", "ai_analysis": "AI分析详情",
        "transfer_cost": "调拨总成本", "waiting_cost": "缺货停工等待成本",
        "net_benefit": "净收益", "recommendation": "AI建议", "status": "调拨状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "stagnant_alerts": {
        "spare_part_id": "备件ID", "warehouse_id": "仓库ID", "quantity": "呆滞数量",
        "stagnant_days": "呆滞天数", "ai_prediction_days": "AI预测即将呆滞天数",
        "ai_suggestion": "AI处理建议", "transfer_suggestion": "调拨建议", "status": "预警状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "suppliers": {
        "code": "供应商编码", "name": "供应商名称", "contact_person": "联系人",
        "contact_phone": "联系电话", "email": "邮箱", "address": "地址",
        "delivery_on_time_rate": "交付准时率", "quality_pass_rate": "质量合格率",
        "comprehensive_score": "综合评分", "risk_level": "风险等级",
        "risk_tags": "风险标签", "last_risk_check": "最后风险检查时间",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "supplier_categories": {
        "supplier_id": "供应商ID", "category": "供应品类", "is_qualified": "是否合格",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "quotations": {
        "quotation_no": "报价单号", "supplier_id": "供应商ID", "purchase_request_id": "关联采购申请ID",
        "items": "报价明细", "raw_file_path": "原始文件路径", "ocr_status": "OCR状态",
        "ocr_confidence": "OCR置信度", "status": "报价状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "price_comparisons": {
        "comparison_no": "比价单号", "spare_part_id": "备件ID",
        "quotation_ids": "参与比价报价单ID列表", "comparison_result": "比价结果",
        "created_by": "创建人ID",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "contracts": {
        "contract_no": "合同编号", "supplier_id": "供应商ID", "title": "合同标题",
        "file_path": "文件路径", "ai_review_status": "AI审查状态",
        "ai_review_result": "AI审查结果", "signed_at": "签订日期", "expiry_date": "到期日期",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "supplier_risk_alerts": {
        "supplier_id": "供应商ID", "alert_type": "预警类型", "severity": "严重程度",
        "title": "预警标题", "content": "预警详情", "source": "信息来源",
        "ai_suggestion": "AI建议措施", "is_read": "是否已读",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "commodity_prices": {
        "commodity_code": "商品编码", "commodity_name": "商品名称", "price": "当前价格",
        "currency": "货币单位", "unit": "单位", "change_percent": "涨跌幅", "trend": "趋势",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "sourcing_recommendations": {
        "spare_part_id": "备件ID", "specification": "规格书内容",
        "recommendations": "推荐供应商列表",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "approval_records": {
        "approval_no": "审批单号", "business_type": "业务类型", "business_id": "业务ID",
        "applicant_id": "申请人ID", "approver_id": "审批人ID", "ai_summary": "AI审批摘要",
        "ai_recommendation": "AI建议", "ai_detail": "AI分析详情",
        "approver_decision": "审批人决策", "approver_comment": "审批意见", "status": "审批状态",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "cost_analyses": {
        "equipment_id": "设备ID", "purchase_cost": "采购成本", "total_repair_labor": "累计维修人工",
        "total_parts_cost": "累计备件消耗", "total_downtime_loss": "累计停机损失",
        "lcc_total": "LCC全生命周期成本", "ai_health_score": "AI健康度评分",
        "ai_recommendation": "AI建议", "ai_report": "AI详细报告", "analyzed_at": "分析日期",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
    "engineer_dispatches": {
        "engineer_id": "工程师ID", "engineer_name": "工程师姓名", "engineer_skill": "工程师技能",
        "location": "维修地点", "distance": "距离公里", "task_desc": "任务描述",
        "status": "调派状态", "supervisor_id": "主管ID", "supervisor_name": "主管姓名",
        "id": "ID", "created_at": "创建时间", "updated_at": "更新时间"
    },
}


async def migrate_table(conn, old_table, new_table, col_map):
    # Disable FK checks for this session
    await conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

    # Check if old table exists
    result = await conn.execute(text(f"SHOW TABLES LIKE '{old_table}'"))
    if not result.fetchone():
        print(f"[SKIP] Old table '{old_table}' does not exist")
        return

    # Check if new table exists
    result = await conn.execute(text(f"SHOW TABLES LIKE '{new_table}'"))
    if not result.fetchone():
        print(f"[SKIP] New table '{new_table}' does not exist")
        return

    # Get old table columns
    result = await conn.execute(text(f"DESCRIBE {old_table}"))
    old_cols = [row[0] for row in result.fetchall()]

    # Get new table columns
    result = await conn.execute(text(f"DESCRIBE {new_table}"))
    new_cols = [row[0] for row in result.fetchall()]

    # Build select and insert columns
    select_cols = []
    insert_cols = []
    for old_col in old_cols:
        new_col = col_map.get(old_col, old_col)
        if new_col in new_cols:
            select_cols.append(f"`{old_col}`")
            insert_cols.append(f"`{new_col}`")
        else:
            print(f"  [WARN] Column '{old_col}' -> '{new_col}' not in new table, skipping")

    if not select_cols:
        print(f"[SKIP] No matching columns for '{old_table}' -> '{new_table}'")
        return

    # Check if new table already has data
    result = await conn.execute(text(f"SELECT COUNT(*) FROM `{new_table}`"))
    count = result.scalar()
    if count > 0:
        print(f"[SKIP] New table '{new_table}' already has {count} rows")
        return

    # Migrate data
    select_sql = f"SELECT {', '.join(select_cols)} FROM `{old_table}`"
    insert_sql = f"INSERT INTO `{new_table}` ({', '.join(insert_cols)}) VALUES ({', '.join([f':{c.strip(chr(96))}' for c in insert_cols])})"

    result = await conn.execute(text(select_sql))
    rows = result.fetchall()

    if not rows:
        print(f"[OK] '{old_table}' -> '{new_table}': 0 rows migrated (source empty)")
        return

    for row in rows:
        params = {insert_cols[i].strip('`'): row[i] for i in range(len(insert_cols))}
        await conn.execute(text(insert_sql), params)

    print(f"[OK] '{old_table}' -> '{new_table}': {len(rows)} rows migrated")


# Tables without foreign keys first, then tables with FKs
MIGRATION_ORDER = [
    ("users", "用户"),
    ("skill_records", "技能记录"),
    ("exam_records", "考核记录"),
    ("equipments", "设备"),
    ("spare_parts", "备件"),
    ("warehouses", "仓库"),
    ("suppliers", "供应商"),
    ("commodity_prices", "大宗商品价格"),
    ("work_orders", "工单"),
    ("inspection_records", "巡检记录"),
    ("maintenance_plans", "维护计划"),
    ("bom_items", "BOM清单"),
    ("inventory_records", "库存记录"),
    ("requisitions", "申购单"),
    ("transfer_orders", "调拨单"),
    ("stagnant_alerts", "呆滞预警"),
    ("supplier_categories", "供应商品类"),
    ("quotations", "报价单"),
    ("price_comparisons", "比价记录"),
    ("contracts", "合同"),
    ("supplier_risk_alerts", "供应商风险预警"),
    ("sourcing_recommendations", "寻源推荐"),
    ("approval_records", "审批记录"),
    ("cost_analyses", "成本分析"),
    ("engineer_dispatches", "工程师调派"),
]


async def main():
    async with engine.begin() as conn:
        for old_table, new_table in MIGRATION_ORDER:
            col_map = COLUMN_MAP.get(old_table, {})
            await migrate_table(conn, old_table, new_table, col_map)
    print("\n[DONE] Migration completed!")


if __name__ == "__main__":
    asyncio.run(main())
