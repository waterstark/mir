import datetime

from fastapi.websockets import WebSocket
from orjson import orjson
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.chat.redis import get_message_pk
from src.chat.schemas import MessageResponse, WSMessageRequest
from src.chat.util import MessageStatus, WSAction, WSStatus, ws_manager


async def websocket_chat(ws: WebSocket):
    user_id = await ws_manager.connect(ws)
    if user_id is None:
        await ws.close()
        return

    while True:
        try:
            b_data = await ws.receive_bytes()
            data = orjson.loads(b_data)
            ws_msg = WSMessageRequest.parse_obj(data)
            # TODO: create separate method for each action
            match ws_msg.action:
                case WSAction.CREATE:
                    ws_msg.message.id = await get_message_pk()
                    msg = MessageResponse(
                        **dict(ws_msg.message),
                        status=MessageStatus.SENT,
                        created_at=datetime.datetime.utcnow(),
                    )
                    # TODO: save message to redis
                    await ws.send_bytes(orjson.dumps({
                        "status": WSStatus.OK,
                        "message": msg.dict(),
                    }))
                case WSAction.DELETE:
                    pass
                case WSAction.UPDATE:
                    pass
        except (RuntimeError, WebSocketDisconnect):  # ws connection error or
            ws_manager.disconnect(user_id)
            break
        except ValidationError:  # pydantic schema parse error + unknown action
            await ws.send_bytes(orjson.dumps({
                "status": WSStatus.ERROR,
                "detail": "unknown message format or action",
            }))

    await ws.close()
