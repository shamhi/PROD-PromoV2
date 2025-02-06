from typing import AsyncIterable

from redis.asyncio import Redis


async def get_redis(host: str, port: int, db: int = 0, decode_responses: bool = True) -> AsyncIterable[Redis]:
    redis_client = Redis(host=host, port=port, db=db, decode_responses=decode_responses)

    try:
        await redis_client.ping()
        yield redis_client
    finally:
        await redis_client.close()
