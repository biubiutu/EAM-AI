"""
迁移脚本: 为设备表添加新字段（入库放置地点、报废地点、状态变更时间、状态备注）
运行: python -m app.migrate_equipment_fields
"""
import asyncio
from app.core.database import engine
from sqlalchemy import text


async def migrate():
    async with engine.connect() as conn:
        existing = await conn.execute(
            text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'eam_ai' AND TABLE_NAME = '设备'")
        )
        cols = {row[0] for row in existing.fetchall()}

        stmts = []
        if "入库放置地点" not in cols:
            stmts.append("ALTER TABLE `设备` ADD COLUMN `入库放置地点` VARCHAR(200) COMMENT '入库放置地点'")
        if "报废地点" not in cols:
            stmts.append("ALTER TABLE `设备` ADD COLUMN `报废地点` VARCHAR(200) COMMENT '报废地点'")
        if "状态变更时间" not in cols:
            stmts.append("ALTER TABLE `设备` ADD COLUMN `状态变更时间` DATETIME COMMENT '状态变更时间'")
        if "状态备注" not in cols:
            stmts.append("ALTER TABLE `设备` ADD COLUMN `状态备注` VARCHAR(500) COMMENT '状态备注'")

        if stmts:
            for s in stmts:
                await conn.execute(text(s))
            await conn.commit()
            for s in stmts:
                print(f"[OK] {s}")
        else:
            print("[SKIP] 所有字段已存在")

    # 用户表: 工程师等级与经验值
    async with engine.connect() as conn:
        existing = await conn.execute(
            text("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'eam_ai' AND TABLE_NAME = '用户'")
        )
        cols = {row[0] for row in existing.fetchall()}

        stmts = []
        if "工程师等级" not in cols:
            stmts.append("ALTER TABLE `用户` ADD COLUMN `工程师等级` VARCHAR(20) DEFAULT 'junior' COMMENT '工程师等级(junior/intermediate/senior/expert)'")
        if "经验值" not in cols:
            stmts.append("ALTER TABLE `用户` ADD COLUMN `经验值` INT DEFAULT 0 COMMENT '经验值'")

        if stmts:
            for s in stmts:
                await conn.execute(text(s))
            await conn.commit()
            for s in stmts:
                print(f"[OK] {s}")
        else:
            print("[SKIP] 用户表字段已存在")


if __name__ == "__main__":
    asyncio.run(migrate())