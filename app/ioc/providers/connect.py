from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import AntifraudConfig, PostgresConfig, RedisConfig
from app.database.postgres.session import create_engine
from app.database.redis.session import get_redis
from app.utils.db_uri import is_valid_postgres_uri


class PostgresProvider(Provider):
    scope = Scope.APP

    @provide
    async def create_db_engine(self, config: PostgresConfig) -> AsyncIterable[AsyncEngine]:
        DB_URI = config.POSTGRES_CONN.replace("postgresql://", "postgresql+asyncpg://")
        if not is_valid_postgres_uri(config.POSTGRES_CONN):
            host = config.POSTGRES_HOST
            port = config.POSTGRES_PORT
            username = config.POSTGRES_USERNAME
            password = config.POSTGRES_PASSWORD
            db_name = config.POSTGRES_DATABASE

            DB_URI = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"

        async for engine in create_engine(DB_URI=DB_URI):
            yield engine


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def create_redis_client(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async for redis in get_redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
        ):
            yield redis


class AntifraudProvider(Provider):
    scope = Scope.APP

    @provide
    async def create_http_client(self, config: AntifraudConfig) -> AsyncIterable[AsyncClient]:
        async with AsyncClient(base_url=f"http://{config.ANTIFRAUD_ADDRESS}") as client:
            yield client
