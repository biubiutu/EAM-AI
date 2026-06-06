"""
删除英文表及不完整中文表，按模型重建全部中文表。
Usage: py -3 -m app.rebuild_cn_tables
"""
import asyncio
from sqlalchemy import text

from app.core.database import engine
from app.models.base import Base
import app.models  # noqa: F401 — 注册全部模型

EN_TABLES = [
    "users", "skill_records", "exam_records", "equipments", "bom_items",
    "work_orders", "inspection_records", "maintenance_plans", "spare_parts",
    "warehouses", "inventory_records", "requisitions", "transfer_orders",
    "stagnant_alerts", "suppliers", "supplier_categories", "quotations",
    "price_comparisons", "contracts", "supplier_risk_alerts",
    "commodity_prices", "sourcing_recommendations", "approval_records",
    "cost_analyses", "engineer_dispatches",
]

CN_TABLES = [
    "用户", "技能记录", "考核记录", "设备", "BOM清单", "工单", "巡检记录", "维护计划",
    "备件", "仓库", "库存记录", "申购单", "调拨单", "呆滞预警", "供应商", "供应商品类",
    "报价单", "比价记录", "合同", "供应商风险预警", "大宗商品价格", "寻源推荐",
    "审批记录", "成本分析", "工程师调派",
]

# 历史迁移遗留的异常表名
LEGACY_TABLES = ["bom清单"]


async def drop_tables(conn, tables: list[str]) -> None:
    result = await conn.execute(text("SHOW TABLES"))
    existing = {row[0] for row in result}
    for table in tables:
        if table in existing:
            await conn.execute(text(f"DROP TABLE `{table}`"))
            print(f"[OK] 已删除表: {table}")
        else:
            print(f"[SKIP] 表不存在: {table}")


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        print("=" * 50)
        print("删除英文表...")
        await drop_tables(conn, EN_TABLES)
        print("删除旧中文表（准备重建）...")
        await drop_tables(conn, CN_TABLES + LEGACY_TABLES)
        await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    async with engine.begin() as conn:
        print("创建中文表...")
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(text("SHOW TABLES"))
        tables = sorted(row[0] for row in result)
        print("=" * 50)
        print(f"[DONE] 当前数据库共 {len(tables)} 张表:")
        for table in tables:
            print(f"  - {table}")


if __name__ == "__main__":
    asyncio.run(main())
