import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, Any

import orjson
from fastapi import Depends, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from src.auth import utils as auth_utils
from src.auth.crud import get_user
from src.auth.models import AuthUser
from src.database import get_async_session


def orjson_dumps(data: Any, **kwargs: Any):
    return orjson.dumps(data, **kwargs).decode("utf-8")


async def get_user_from_ws_cookie(
        ws: WebSocket,
        session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AsyncGenerator[AuthUser, None]:
    cookies = ws.cookies.get("mir")
    cookies_data = auth_utils.decode_jwt(cookies)
    user = await get_user(cookies_data.get("email"), session)
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
