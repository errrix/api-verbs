import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Конвертация URL для asyncpg (если Render дает postgres://)
database_url = settings.database_url
print(f"Original DATABASE_URL: {database_url[:50]}...")  # Debug

# Конвертация postgresql:// и postgres:// в postgresql+asyncpg://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"Converted DATABASE_URL: {database_url[:50]}...")  # Debug

# Создание асинхронного движка для PostgreSQL
engine = create_async_engine(
    database_url,
    echo=True,
    future=True
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_db():
    """Dependency для получения сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


