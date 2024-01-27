import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, Any

import orjson
from fastapi import Depends, WebSocketException
from starlette.websockets import WebSocket

from src.auth.base_config import current_user
from src.auth.models import AuthUser
from src.auth.schemas import UserSchema


def orjson_dumps(data: Any, **kwargs: Any):
    return orjson.dumps(data, **kwargs).decode("utf-8")


async def get_user_from_ws_cookie(
        ws: WebSocket,
        user: Annotated[UserSchema, Depends(current_user)],
) -> AsyncGenerator[AuthUser, None]:
    ws.cookies.get("mir")
    # TODO user = await auth_backend.get_strategy().read_token(cookie, user_manager)
    if not user or not user.is_active:
        raise WebSocketException(404, "Invalid user")
    yield user


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, WebSocket] = {}

    async def connect(self, ws: WebSocket, user: AuthUser) -> None:
        """
        Accept WebSocket and add connection for particular user to active_connections
        to insta-message them.
        """

        await ws.accept()
        self.active_connections[user.id] = ws
        # TODO: bg_task get last user's ~10-20 matches and save to redis

    async def disconnect(self, ws: WebSocket, user_id: uuid.UUID):
        self.active_connections.pop(user_id, None)
        await ws.close()


ws_manager = WebSocketConnectionManager()
