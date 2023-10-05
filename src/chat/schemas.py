import datetime
import uuid

from pydantic import BaseModel

from src.chat.util import MessageStatus, WSAction, WSStatus


class BaseMessage(BaseModel):
    match_id: uuid.UUID
    from_id: uuid.UUID
    text: str

    class Config:
        orm_mode = True


class MessageRequest(BaseMessage):
    id: uuid.UUID | None


class MessageResponse(BaseMessage):
    id: uuid.UUID
    created_at: datetime.datetime
    status: MessageStatus


class WSMessageRequest(BaseModel):
    action: WSAction
    message: MessageRequest

    class Config:
        orm_mode = True


class WSMessageResponse(BaseModel):
    status: WSStatus
    detail: str | None
    message: MessageResponse

    class Config:
        orm_mode = True
