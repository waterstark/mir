import json
import uuid

import orjson
import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsStr, IsUUID

from src.auth.models import AuthUser
from src.chat.schemas import MessageCreateRequest, MessageStatus, WSAction, WSStatus
from src.chat.utils import orjson_dumps
from src.matches.models import Match
from src.mongodb.mongodb import Mongo
from src.redis.redis import redis


async def test_ws_msg_create(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    match: Match,
):
    msg = {"match_id": match.id, "text": "lol",
           "from_id": user.id, "to_id": user2.id}

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.CREATE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.OK
    assert resp["message"] == {
        "id": IsUUID(),
        "match_id": IsUUID(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "lol",
        "status": str(MessageStatus.SENT),
        "updated_at": IsStr(),
    }

    cache_match = await redis.get(f'match_{resp["message"]["match_id"]}')

    assert json.loads(cache_match)["match_id"] == resp["message"]["match_id"]


async def test_ws_connect_without_token(async_client: TestClient):
    """App does not accept ws connection if there is no token."""
    await async_client.get("/api/v1/auth/logout")
    with pytest.raises(TypeError) as exc:
        async with async_client.websocket_connect("/chat/ws"):
            pass
    assert str(exc.value) == "'Message' object is not subscriptable"


async def test_ws_msg_create_without_match(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user3: AuthUser,
):
    msg = {"match_id": uuid.uuid4(), "text": "kek",
           "from_id": user.id, "to_id": user3.id}

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.CREATE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == f"No match for users {user.id} and {user3.id}"


async def test_ws_unknown_action(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    match: Match,
):
    msg = {"match_id": match.id, "text": "lol",
           "from_id": user.id, "to_id": user2.id}

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "user_id": user.id,
        }))
        await ws.send_text(orjson_dumps({
            "action": "DO SOME SHIT",
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == "unknown action or bad message format"


async def test_ws_message_delete(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    mongo: Mongo,
    match: Match,
):
    msg = {
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "aaa",
    }

    result = await mongo.create_message(MessageCreateRequest(**msg))

    msg["id"] = result.id
    msg.pop("text")

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.DELETE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.OK


async def test_ws_unknown_message_delete(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    match: Match,
):
    msg = {
        "id": uuid.uuid4(),
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
    }

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.DELETE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == f"unknown message id {msg['id']}"


async def test_ws_message_update(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    mongo: Mongo,
    match: Match,
):
    msg = {
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "kek",
        "status": MessageStatus.SENT,
    }

    msg = await mongo.create_message(MessageCreateRequest(**msg))
    msg.text = "lol"
    msg.status = MessageStatus.READ

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.UPDATE,
            "message": msg.dict(exclude={"updated_at"}),
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.OK
    assert resp["message"] == {
        "id": IsUUID(),
        "match_id": IsUUID(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "lol",
        "status": str(MessageStatus.READ),
        "updated_at": IsStr(),
    }


async def test_ws_unknown_message_update(
    async_client: TestClient,
    user: AuthUser,
    authorised_cookie: dict,
    user2: AuthUser,
    match: Match,
):
    msg = {
        "id": uuid.uuid4(),
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "kek",
        "status": MessageStatus.READ,
    }

    async with async_client.websocket_connect("/chat/ws", cookies=authorised_cookie) as ws:
        await ws.send_text(orjson_dumps({
            "action": WSAction.UPDATE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_text())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == f"unknown message id {msg['id']}"
