import uuid
from unittest import mock

import orjson
import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsStr, IsUUID

from src.auth.models import AuthUser
from src.chat.routers import ws_manager
from src.chat.schemas import MessageCreateRequest
from src.chat.util import MessageStatus, WSAction, WSStatus
from src.mongodb.mongodb import Mongo


async def test_ws_msg_create(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
):
    msg = {"match_id": uuid.uuid4(), "text": "lol",
           "from_id": user.id, "to_id": user2.id}

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": WSAction.CREATE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

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


async def test_ws_bad_user_credentials(async_client: TestClient):
    with mock.patch.object(ws_manager, "parse_user_id_on_connect", return_value=None):
        async with async_client.websocket_connect("/chat/ws") as ws:
            await ws.send_bytes(orjson.dumps({
                "user_id": uuid.uuid4(),
            }))
            await ws.send_bytes(orjson.dumps({
                "action": WSAction.CREATE,
                "message": {},
            }))

            # websocket raises "Exception", so here it is
            with pytest.raises(Exception) as exc:  # noqa: PT011
                await ws.receive_bytes()

    assert str(exc.value) == "{'type': 'websocket.close', 'code': 1000, 'reason': ''}"


async def test_ws_unknown_action(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
):
    msg = {"match_id": uuid.uuid4(), "text": "lol",
           "from_id": user.id, "to_id": user2.id}

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": "DO SOME SHIT",
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == "unknown action or message format"


async def test_ws_message_delete(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
        mongo: Mongo,
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

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": WSAction.DELETE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

    assert resp["status"] == WSStatus.OK


async def test_ws_message_wrong_delete(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
):
    msg = {
        "id": uuid.uuid4(),
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
    }

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": WSAction.DELETE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == f"unknown message id {msg['id']}"


async def test_ws_message_update(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
        mongo: Mongo,
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

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": WSAction.UPDATE,
            "message": msg.dict(exclude={"updated_at"}),
        }))
        resp = orjson.loads(await ws.receive_bytes())

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


async def test_ws_message_update_error(
        async_client: TestClient,
        user: AuthUser,
        user2: AuthUser,
):
    msg = {
        "id": uuid.uuid4(),
        "match_id": uuid.uuid4(),
        "from_id": user.id,
        "to_id": user2.id,
        "text": "kek",
        "status": MessageStatus.READ,
    }

    async with async_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": WSAction.UPDATE,
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == f"unknown message id {msg['id']}"
