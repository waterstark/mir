from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from orjson import JSONEncodeError, orjson
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.auth.models import AuthUser
from src.chat.exceptions import NoMatchError
from src.chat.schemas import WSAction, WSMessageRequest, WSStatus
from src.chat.utils import (
    create_message,
    delete_message,
    get_user_from_ws_cookie,
    orjson_dumps,
    update_message,
    ws_manager,
)

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
