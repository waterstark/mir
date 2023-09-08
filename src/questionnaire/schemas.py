import uuid

from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    class Config:
        orm_mode = True


class UserQuestionnaireHobby(UserBaseSchema):
    hobby_name: str


class UserQuestionnaireHobbyResponse(UserQuestionnaireHobby):
    id: uuid.UUID | None = None


class UserQuestionnaireSchema(UserBaseSchema):
    id: uuid.UUID | None = None
    firstname: str
    lastname: str
    gender: str
    photo: str
    country: str
    city: str
    about: str
    hobbies: list[UserQuestionnaireHobby]
    height: int
    goals: str
    body_type: str


class UserQuestionnaireResponse(UserBaseSchema):
    id: uuid.UUID
    firstname: str
    lastname: str
    gender: str
    photo: str
    country: str
    city: str
    about: str
    hobbies: list[UserQuestionnaireHobbyResponse]
    height: int
    goals: str
    body_type: str
    is_match: bool = False
