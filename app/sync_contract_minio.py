"""
将数据库「合同」表记录同步到 MinIO（按文件路径精准匹配对象名）
Usage: py -3 -m app.sync_contract_minio
"""
import asyncio

from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.purchase import Contract
from app.services.contract_storage import sync_contracts_to_minio


async def main():
    async with async_session_factory() as session:
        result = await session.execute(select(Contract))
        contracts = result.scalars().all()
        if not contracts:
            print("[WARN] 合同表无数据，请先运行 py -3 -m app.init_data")
            return
        stats = sync_contracts_to_minio(contracts)
        print(f"[OK] 合同 MinIO 同步完成：已同步 {stats['已同步']} 个，跳过 {stats['已跳过']} 个")
        if stats["错误"]:
            for err in stats["错误"]:
                print(f"  [ERROR] {err}")


if __name__ == "__main__":
    asyncio.run(main())
