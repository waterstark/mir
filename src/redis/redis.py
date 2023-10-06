import os
from typing import Any

import aioredis


class Redis:
    path_to_conf_file = "/etc/redis/redis.conf"

    def __init__(self):
        self.redis_client = aioredis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=0,
            decode_responses=True,
        )

    async def get(self, name: str, key: str):
        data: dict = await self.redis_client.hget(name=name, key=key)
        if data:
            return data
        return None

    async def set(self, name: str, key: str, value: Any):
        await self.redis_client.hset(name=name, key=key, value=value)

    async def delete(self, name: str):
        await self.redis_client.hdel(name)


redis = Redis()
