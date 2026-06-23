import sys
sys.path.insert(0, 'D:\\EAM-AI')
import asyncio
from app.core.database import engine
from app.models.base import Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created/updated")

asyncio.run(create_tables())
