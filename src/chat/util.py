import uuid
from enum import Enum

import orjson
from fastapi.websockets import WebSocket


class MessageStatus(str, Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    DELETED = "DELETED"

    def __str__(self):
        return self


class WSAction(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"


class WSStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, WebSocket] = {}

    async def connect(self, ws: WebSocket) -> uuid.UUID | None:
        """
        Connect and receive first message with credentials.
        Then use it through all the connection.
        """
        await ws.accept()
        user_id = self.parse_user_id_on_connect(await ws.receive_bytes())
        if user_id is not None:
            self.active_connections[user_id] = ws
        # TODO: get user's matches and save to redis
        return user_id

    # TODO: change to jwt parse when ready
    def parse_user_id_on_connect(self, b_data: bytes) -> uuid.UUID | None:
        data = orjson.loads(b_data)
        return data.get("user_id")

    def disconnect(self, user_id: uuid.UUID):
        self.active_connections.pop(user_id, None)


ws_manager = WebSocketConnectionManager()
