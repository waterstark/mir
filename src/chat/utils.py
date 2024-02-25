import asyncio
import datetime
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, Any

import orjson
from fastapi import Depends, WebSocketException
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from src.auth.base_config import get_auth_user
from src.auth.models import AuthUser
from src.chat.exceptions import NoMatchError
from src.chat.redis import get_match
from src.chat.schemas import (
    MessageCreateRequest,
    MessageDeleteRequest,
    MessageDeleteResponse,
    MessageResponse,
    MessageUpdateRequest,
    WSAction,
    WSMessageRequest,
    WSMessageResponse,
    WSStatus,
)
from src.database import async_session_maker, get_async_session, mongo


def orjson_dumps(data: Any, **kwargs: Any):
    if isinstance(data, BaseModel):
        data = data.dict()
    return orjson.dumps(data, **kwargs).decode("utf-8")


async def get_user_from_ws_cookie(
        ws: WebSocket,
        session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AsyncGenerator[AuthUser, None]:
    user = await get_auth_user(ws.cookies.get("mir"), session)
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

    def find_users_ws(self, id: uuid.UUID):
        return self.active_connections.get(id)


async def send_insta_message(msg: str, to_id: uuid.UUID):
    ws = ws_manager.find_users_ws(to_id)
    if ws is not None:
        await ws.send_text(msg)


async def send_ws_message(
        ws: WebSocket,
        msg: MessageResponse | MessageDeleteResponse,
        action: WSAction,
        status: WSStatus = WSStatus.OK,
):
    to_id = msg.to_id
    msg = orjson_dumps(WSMessageResponse(
        status=status,
        action=action,
        message=msg,
    ))

    await asyncio.gather(
        ws.send_text(msg),
        send_insta_message(msg, to_id),
    )


async def create_message(ws_msg: WSMessageRequest, ws: WebSocket, user: AuthUser):
    if not isinstance(ws_msg.message, MessageCreateRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can send message to 'to_id'
    async with async_session_maker() as session:
        match = await get_match(session, user, ws_msg)

    if match is None:
        raise NoMatchError(user.id, ws_msg.message.to_id)

    msg = await mongo.create_message(ws_msg.message)

    await send_ws_message(ws, MessageResponse.parse_obj(msg), WSAction.CREATE)
    # TODO: manage/log exceptions from 'gather' result if occur


async def delete_message(ws_msg: WSMessageRequest, ws: WebSocket, user: AuthUser):
    if not isinstance(ws_msg.message, MessageDeleteRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can delete message to 'to_id'
    async with async_session_maker() as session:
        match = await get_match(session, user, ws_msg)

    if match is None:
        raise NoMatchError(user.id, ws_msg.message.to_id)

    result = await mongo.delete_message(ws_msg.message.id)

    if not result.deleted_count:
        await ws.send_text(orjson_dumps(WSMessageResponse(
            status=WSStatus.ERROR,
            action=WSAction.DELETE,
            detail=f"unknown message id {ws_msg.message.id}",
        )))
        return

    await send_ws_message(ws, MessageDeleteResponse.parse_obj(ws_msg.message), WSAction.DELETE)


async def update_message(ws_msg: WSMessageRequest, ws: WebSocket, user: AuthUser):
    if not isinstance(ws_msg.message, MessageUpdateRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can send message to 'to_id'
    async with async_session_maker() as session:
        match = await get_match(session, user, ws_msg)

    if match is None:
        raise NoMatchError(user.id, ws_msg.message.to_id)

    result = await mongo.get_message(ws_msg.message.id)
    if result is None:
        await ws.send_text(orjson_dumps({
            "status": WSStatus.ERROR,
            "action": WSAction.UPDATE,
            "detail": f"unknown message id {ws_msg.message.id}",
        }))
        return

    msg = MessageResponse(
        **ws_msg.message.dict(),
        created_at=result["created_at"],
        updated_at=datetime.datetime.utcnow(),
    )

    result = await mongo.update_message(msg)
    if not result.modified_count:
        await ws.send_text(orjson_dumps(WSMessageResponse(
            status=WSStatus.ERROR,
            action=WSAction.UPDATE,
            detail=f"error updating message id {msg.id}",
        )))
        return

    await send_ws_message(ws, msg, WSAction.UPDATE)


ws_manager = WebSocketConnectionManager()
