import datetime

from pydantic import BaseModel
from pydantic.types import UUID4


class UserLikeBase(BaseModel):
    user_id: UUID4
    liked_user_id: UUID4

    class Config:
        orm_mode = True


class UserLikeRequest(UserLikeBase):
    pass


class UserLikeResponse(UserLikeBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
