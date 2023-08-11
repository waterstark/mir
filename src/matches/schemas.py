from pydantic import BaseModel
from pydantic.types import UUID4


class MatchRequest(BaseModel):
    user1_id: UUID4
    user2_id: UUID4

    class Config:
        orm_mode = True
