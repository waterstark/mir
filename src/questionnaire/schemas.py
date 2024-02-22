import uuid
from datetime import date

from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    class Config:
        orm_mode = True


class UserHobby(UserBaseSchema):
    hobby_name: str


class CreateUserQuestionnaireSchema(UserBaseSchema):
    firstname: str
    lastname: str
    gender: str
    photo: str
    country: str
    city: str
    about: str
    hobbies: list[UserHobby]
    sport: str
    alcohol: str
    smoking: str
    height: int
    goals: str
    birthday: date


class ResponseUserQuestionnaireSchema(CreateUserQuestionnaireSchema):
    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class ResponseQuestionnaireSchemaWithMatch(ResponseUserQuestionnaireSchema):
    is_match: bool = False
    match_id: uuid.UUID | None = None
