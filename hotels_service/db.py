from aioredis import Redis
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from hotels_service.config import settings

DATABASE_URL = settings.DATABASE_URL
DATABASE_PARAMS = {}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)  # движок

# генератор сессий; expire_on_commit - завершение транзакций
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):  # для миграций, здесь аккумулируются все данные
    pass


async def get_redis():
    redis = await aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    try:
        yield redis
    finally:
        await redis.close()
