import uuid

from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    class Config:
        orm_mode = True


class CreateUserQuestionnaireSchema(UserBaseSchema):
    firstname: str
    lastname: str
    gender: str
    photo: str
    country: str
    city: str
    about: str
    passion: str
    height: int
    goals: str
    body_type: str
    user_id: uuid.UUID


class ResponseUserQuestionnaireSchema(CreateUserQuestionnaireSchema):
    id: uuid.UUID | None = None
