import uuid

from fastapi_users import schemas


class UserCreateOutput(schemas.BaseUser[int]):
    id: uuid.UUID
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreateInput(schemas.BaseUserCreate):
    email: str
    password: str
