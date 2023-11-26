import uuid

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
    height: int
    goals: str
    body_type: str


class ResponseUserQuestionnaireSchema(CreateUserQuestionnaireSchema):
    id: uuid.UUID | None = None


class ResponseQuestionnaireSchemaWithMatch(ResponseUserQuestionnaireSchema):
    is_match: bool = False
