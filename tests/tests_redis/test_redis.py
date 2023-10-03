import aioredis

from tests.fixtures import data_for_redis


async def test_redis_set(redis_client: aioredis):
    await redis_client.set("TO_user_id", data_for_redis["TO_user_id"])
    response: dict = await redis_client.get("TO_user_id")
    assert response == {
        "message_update": ["Message(содержит from_user_id)"],
        "message_delete": ["message_id"],
        "message_create": ["Message"],
    }


async def test_redis_get(redis_client: aioredis):
    response: dict = await redis_client.get("TO_user_id")
    assert response == {
        "message_update": ["Message(содержит from_user_id)"],
        "message_delete": ["message_id"],
        "message_create": ["Message"],
    }


async def test_redis_delete(redis_client: aioredis):
    await redis_client.delete("TO_user_id")
    try_to_get: bool = await redis_client.get("TO_user_id")
    assert try_to_get is None
