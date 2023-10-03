import json
import os
from typing import Any

import aioredis


class Redis:
    path_to_conf_file = "/etc/redis/redis.conf"

    def __init__(self):
        self.redis_client = aioredis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=6379,
            db=0,
            decode_responses=True,
        )

    async def get(self, key: str):
        cached_data = await self.redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set(self, key: str, value: Any):
        value_to_string = json.dumps(value)
        await self.redis_client.set(key, value_to_string)

    async def delete(self, key: str):
        await self.redis_client.delete(key)
