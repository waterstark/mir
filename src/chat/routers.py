import datetime

from fastapi.websockets import WebSocket
from orjson import orjson
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.chat.schemas import (
    MessageCreateRequest,
    MessageDeleteRequest,
    MessageResponse,
    MessageUpdateRequest,
    WSMessageRequest,
)
from src.chat.util import WSAction, WSStatus, ws_manager
from src.database import mongo


async def websocket_chat(ws: WebSocket):
    user_id = await ws_manager.connect(ws)
    if user_id is None:
        await ws.close()
        return

    # TODO: recieve message updates

    while True:
        try:
            b_data = await ws.receive_bytes()
            data = orjson.loads(b_data)
            ws_msg = WSMessageRequest.parse_obj(data)
            match ws_msg.action:
                case WSAction.CREATE:
                    await create_message(ws_msg, ws)
                case WSAction.DELETE:
                    await delete_message(ws_msg, ws)
                case WSAction.UPDATE:
                    await update_message(ws_msg, ws)
        except (RuntimeError, WebSocketDisconnect):  # ws connection error
            ws_manager.disconnect(user_id)
            break
        except ValidationError:  # pydantic schema parse error + unknown action
            await ws.send_bytes(orjson.dumps({
                "status": WSStatus.ERROR,
                "detail": "unknown action or message format",
            }))

    await ws.close()


async def create_message(ws_msg: WSMessageRequest, ws: WebSocket):
    if not isinstance(ws_msg.message, MessageCreateRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can send message to 'to_id'

    msg = await mongo.create_message(ws_msg.message)

    # TODO: may be create orjson message serializer
    await ws.send_bytes(orjson.dumps({
        "status": WSStatus.OK,
        "message": msg.dict(),
    }))


async def delete_message(ws_msg: WSMessageRequest, ws: WebSocket):
    if not isinstance(ws_msg.message, MessageDeleteRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can delete message to 'to_id'
    result = await mongo.delete_message(ws_msg.message.id)

    if not result.deleted_count:
        await ws.send_bytes(orjson.dumps({
            "status": WSStatus.ERROR,
            "detail": f"unknown message id {ws_msg.message.id}",
        }))

    await ws.send_bytes(orjson.dumps({
        "status": WSStatus.OK,
    }))


async def update_message(ws_msg: WSMessageRequest, ws: WebSocket):
    if not isinstance(ws_msg.message, MessageUpdateRequest):
        raise ValidationError

    # TODO: get user's matches from redis and check if he can send message to 'to_id'

    result = await mongo.get_message(ws_msg.message.id)
    if result is None:
        await ws.send_bytes(orjson.dumps({
            "status": WSStatus.ERROR,
            "detail": f"unknown message id {ws_msg.message.id}",
        }))
        return

    msg = MessageResponse(
        **ws_msg.message.dict(),
        updated_at=datetime.datetime.utcnow(),
    )

    result = await mongo.update_message(msg)
    if not result.modified_count:
        await ws.send_bytes(orjson.dumps({
            "status": WSStatus.OK,
            "detail": f"error updating message id {msg.id}",
        }))

    await ws.send_bytes(orjson.dumps({
        "status": WSStatus.OK,
        "message": msg.dict(),
    }))
