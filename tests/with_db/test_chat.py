import uuid
from unittest import mock

import orjson
import pytest
from async_asgi_testclient import TestClient
from dirty_equals import IsStr, IsUUID

from src.auth.models import AuthUser
from src.chat.routers import ws_manager
from src.chat.util import MessageStatus, WSAction, WSStatus


async def test_ws_msg_create(ws_client: TestClient, user: AuthUser):
    msg = {"match_id": uuid.uuid4(), "from_id": user.id, "text": "lol"}

    async with ws_client.websocket_connect("/chat/ws") as ws:
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
        "text": "lol",
        "status": str(MessageStatus.SENT),
        "created_at": IsStr(),
    }


async def test_ws_bad_user_credentials(ws_client: TestClient):
    with mock.patch.object(ws_manager, "parse_user_id_on_connect", return_value=None):
        async with ws_client.websocket_connect("/chat/ws") as ws:
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


async def test_ws_unknown_action(ws_client: TestClient, user: AuthUser):
    msg = {"match_id": uuid.uuid4(), "from_id": user.id, "text": "lol"}

    async with ws_client.websocket_connect("/chat/ws") as ws:
        await ws.send_bytes(orjson.dumps({
            "user_id": user.id,
        }))
        await ws.send_bytes(orjson.dumps({
            "action": "DO SOME SHIT",
            "message": msg,
        }))
        resp = orjson.loads(await ws.receive_bytes())

    assert resp["status"] == WSStatus.ERROR
    assert resp["detail"] == "unknown message format or action"
