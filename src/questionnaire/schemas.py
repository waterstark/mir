import uuid
from datetime import date

from pydantic import BaseModel

from .params_choice import AlcoholType, Gender, Goal, SmokingType, SportType


class UserBaseSchema(BaseModel):
    class Config:
        orm_mode = True


class UserHobby(UserBaseSchema):
    hobby_name: str


class CreateUserQuestionnaireSchema(UserBaseSchema):
    firstname: str
    lastname: str
    gender: Gender
    photo: str
    country: str
    city: str
    about: str
    hobbies: list[UserHobby]
    sport: SportType
    alcohol: AlcoholType
    smoking: SmokingType
    height: int
    goals: Goal
    birthday: date


class ResponseUserQuestionnaireSchema(CreateUserQuestionnaireSchema):
    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class ResponseQuestionnaireSchemaWithMatch(ResponseUserQuestionnaireSchema):
    is_match: bool = False
    match_id: uuid.UUID | None = None
