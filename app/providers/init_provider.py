from typing import AsyncIterable

from httpx import AsyncClient
from redis.asyncio import Redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.database.postgres.session import create_engine
from app.database.redis.session import get_redis
from app.utils.db_uri import is_valid_postgres_uri


class InitProvider(Provider):
    scope = Scope.APP

    def __init__(self, config: Settings):
        super().__init__()
        self.config = config

    @provide
    async def create_db_engine(self) -> AsyncIterable[AsyncEngine]:
        DB_URI = self.config.POSTGRES_CONN.replace("postgresql://", "postgresql+asyncpg://")
        if not is_valid_postgres_uri(self.config.POSTGRES_CONN):
            host = self.config.POSTGRES_HOST
            port = self.config.POSTGRES_PORT
            username = self.config.POSTGRES_USERNAME
            password = self.config.POSTGRES_PASSWORD
            db_name = self.config.POSTGRES_DATABASE

            DB_URI = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"

        async for engine in create_engine(DB_URI=DB_URI):
            yield engine

    @provide
    async def create_redis_client(self) -> AsyncIterable[Redis]:
        async for redis in get_redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
        ):
            yield redis

    @provide
    async def create_http_client(self) -> AsyncIterable[AsyncClient]:
        async with AsyncClient(base_url=f"http://{self.config.ANTIFRAUD_ADDRESS}") as client:
            yield client
