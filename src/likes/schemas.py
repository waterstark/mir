import datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4


class UserLikeBase(BaseModel):
    user_id: UUID4
    liked_user_id: UUID4
    is_liked: bool = Field(default=False)

    class Config:
        orm_mode = True


class UserLikeRequest(UserLikeBase):
    ...


class UserLikeResponse(UserLikeBase):
    id: UUID4
    created_at: datetime.datetime
