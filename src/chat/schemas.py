import datetime
import uuid

from pydantic import BaseModel

from src.chat.util import MessageStatus, WSAction, WSStatus


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
