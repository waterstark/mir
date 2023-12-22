from typing import Any

import aioredis

from src.config import settings


class Redis:
    path_to_conf_file = "/etc/redis/redis.conf"

    def __init__(self):
        self.redis_client = aioredis.from_url(
            url=settings.db_url_redis,
            db=0,
            decode_responses=True,
        )

    async def get(self, name: str):
        data: dict = await self.redis_client.get(name=name)
        if data:
            return data
        return None

    async def set(self, name: str, value: Any):
        await self.redis_client.set(name=name, value=value, ex=600)

    async def delete(self, name: str):
        await self.redis_client.delete(name)

    async def flush_db(self):
        await self.redis_client.flushdb(asynchronous=True)


redis = Redis()
