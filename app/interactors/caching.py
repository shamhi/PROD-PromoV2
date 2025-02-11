import json
from datetime import datetime
from typing import Optional

from redis.asyncio import Redis

from app.schemas.common import CompanyId, UserId
from app.schemas.user import AntifraudResponse
from app.utils.serializer import serialize_antifraud_response


class CacheAccessTokenInteractor:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = 3600

    async def save_user_token(self, user_id: UserId, token: str) -> None:
        key = f"user_token:{user_id}"
        await self.redis.set(key, token, ex=self.ttl)

    async def get_user_token(self, user_id: UserId) -> str | None:
        key = f"user_token:{user_id}"
        token = await self.redis.get(key)

        if token:
            return token

    async def save_company_token(self, company_id: CompanyId, token: str) -> None:
        key = f"company_token:{company_id}"
        await self.redis.set(key, token, ex=self.ttl)

    async def get_company_token(self, company_id: CompanyId) -> str | None:
        key = f"company_token:{company_id}"
        token = await self.redis.get(key)

        if token:
            return token


class CacheAntifraudInteractor:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_response(self, user_id: UserId, antifraud_response: AntifraudResponse) -> None:
        key = f"antifraud:{user_id}"

        if antifraud_response.cache_until:
            exp = int((antifraud_response.cache_until - datetime.utcnow()).total_seconds())
            if exp > 0:
                cache_data = serialize_antifraud_response(antifraud_response)
                await self.redis.set(key, json.dumps(cache_data), ex=exp)

    async def get_cached_response(self, user_id: UserId) -> AntifraudResponse | None:
        key = f"antifraud:{user_id}"
        cached_data = await self.redis.get(key)

        if cached_data:
            return AntifraudResponse(**json.loads(cached_data))
