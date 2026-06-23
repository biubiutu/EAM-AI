import sys
sys.path.insert(0, 'D:\\EAM-AI')
import asyncio
from app.core.database import engine
from sqlalchemy import text

old_tables = [
    'users', 'skill_records', 'exam_records', 'equipments', 'bom_items',
    'work_orders', 'inspection_records', 'maintenance_plans', 'spare_parts',
    'warehouses', 'inventory_records', 'requisitions', 'transfer_orders',
    'stagnant_alerts', 'suppliers', 'supplier_categories', 'quotations',
    'price_comparisons', 'contracts', 'supplier_risk_alerts',
    'commodity_prices', 'sourcing_recommendations', 'approval_records',
    'cost_analyses', 'engineer_dispatches'
]

async def drop():
    async with engine.begin() as conn:
        await conn.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        for t in old_tables:
            result = await conn.execute(text("SHOW TABLES LIKE '%s'" % t))
            if result.fetchone():
                await conn.execute(text("DROP TABLE `%s`" % t))
                print('[OK] Dropped %s' % t)
            else:
                print('[SKIP] %s not found' % t)
        await conn.execute(text('SET FOREIGN_KEY_CHECKS=1'))
    print('\n[DONE] All old tables dropped')

if __name__ == '__main__':
    asyncio.run(drop())
