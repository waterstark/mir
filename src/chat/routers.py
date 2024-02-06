import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from orjson import JSONEncodeError, orjson
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.auth.models import AuthUser
from src.chat.exceptions import NoMatchError
from src.chat.redis import get_match
from src.chat.schemas import (
    MessageCreateRequest,
    MessageDeleteRequest,
    MessageResponse,
    MessageUpdateRequest,
    WSAction,
    WSMessageRequest,
    WSStatus,
)
from src.chat.utils import get_user_from_ws_cookie, orjson_dumps, ws_manager
from src.database import async_session_maker, mongo

ws_router = APIRouter(
    prefix="/chat",
    tags=["WebSocket chat"],
)


@ws_router.websocket("/ws")
async def websocket_chat(
    ws: WebSocket,
    user: Annotated[AuthUser, Depends(get_user_from_ws_cookie)],
):
    if user is None:
        await ws.close()
        return

    await ws_manager.connect(ws, user)

    # TODO: recieve message updates

    while True:
        try:
            text_data = await ws.receive_text()
            data = orjson.loads(text_data)
            ws_msg = WSMessageRequest.parse_obj(data)
            match ws_msg.action:
                case WSAction.CREATE:
                    await create_message(ws_msg, ws, user)
                case WSAction.DELETE:
                    await delete_message(ws_msg, ws, user)
                case WSAction.UPDATE:
                    await update_message(ws_msg, ws, user)
        except (RuntimeError, WebSocketDisconnect):  # ws connection error
            await ws_manager.disconnect(ws, user.id)
            break
        except (ValidationError, JSONEncodeError):  # pydantic schema parse error, unknown action, decode msg error
            await ws.send_text(orjson_dumps({
                "status": WSStatus.ERROR,
                "detail": "unknown action or bad message format",
            }))
        except NoMatchError as e:
            await ws.send_text(orjson_dumps({
                "status": WSStatus.ERROR,
                "detail": str(e),
            }))
        except Exception:  # noqa: BLE001
            # TODO: log this shit
            await ws_manager.disconnect(ws, user.id)
            break


async def create_message(ws_msg: WSMessageRequest, ws: WebSocket, user: AuthUser):
    if not isinstance(ws_msg.message, MessageCreateRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can send message to 'to_id'
    async with async_session_maker() as session:
        match = await get_match(session, user, ws_msg)

    if match is None:
        raise NoMatchError(user.id, ws_msg.message.to_id)

    msg = await mongo.create_message(ws_msg.message)

    await ws.send_text(orjson_dumps({
        "status": WSStatus.OK,
        "message": msg.dict(),
    }))

    # TODO: add bg task to insta-message who is online


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
        await ws.send_text(orjson_dumps({
            "status": WSStatus.ERROR,
            "detail": f"unknown message id {ws_msg.message.id}",
        }))

    await ws.send_text(orjson_dumps({
        "status": WSStatus.OK,
    }))


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
        await ws.send_text(orjson_dumps({
            "status": WSStatus.OK,
            "detail": f"error updating message id {msg.id}",
        }))

    await ws.send_text(orjson_dumps({
        "status": WSStatus.OK,
        "message": msg.dict(),
    }))
