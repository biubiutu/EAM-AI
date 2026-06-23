from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings

engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=5,
    pool_recycle=3600,
    pool_pre_ping=False,
    connect_args={"connect_timeout": 5},
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()