import datetime
import uuid
from enum import Enum

from pydantic import BaseModel


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


class BaseMessage(BaseModel):
    match_id: uuid.UUID
    from_id: uuid.UUID
    to_id: uuid.UUID

    class Config:
        orm_mode = True


class MessageCreateRequest(BaseMessage):
    text: str


class MessageUpdateRequest(BaseMessage):
    id: uuid.UUID
    status: MessageStatus
    text: str


class MessageDeleteRequest(BaseMessage):
    id: uuid.UUID


class MessageResponse(BaseMessage):
    id: uuid.UUID
    text: str
    updated_at: datetime.datetime
    status: MessageStatus


class WSMessageRequest(BaseModel):
    action: WSAction
    message: MessageUpdateRequest | MessageCreateRequest | MessageDeleteRequest

    class Config:
        orm_mode = True


class WSMessageResponse(BaseModel):
    status: WSStatus
    detail: str | None
    message: MessageResponse | None

    class Config:
        orm_mode = True
