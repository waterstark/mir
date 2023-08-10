import uuid
from datetime import datetime

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, EmailStr, Field, ValidationError, root_validator

from src.auth.models import AGE_MAX, AGE_MIN, RANGE_MAX, RANGE_MIN


class UserCreateOutput(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreateInput(CreateUpdateDictModel):
    email: EmailStr
    password: str


class BaseUserProfile(BaseModel):
    """Base profile model."""

    search_range_min: int = Field(ge=RANGE_MIN, le=RANGE_MAX)
    search_range_max: int = Field(ge=RANGE_MIN, le=RANGE_MAX)
    search_age_min: int = Field(ge=AGE_MIN, le=AGE_MAX)
    search_age_max: int = Field(ge=AGE_MIN, le=AGE_MAX)

    class Config:
        orm_mode = True

    @root_validator
    @classmethod
    def check_sum(cls, values: dict):
        range_min = values.get("search_range_min")
        range_max = values.get("search_range_max")
        age_min = values.get("search_age_min")
        age_max = values.get("search_age_max")
        if range_min > range_max:
            raise ValidationError("Min_range should me less than max_range.")
        if age_min > age_max:
            raise ValidationError("Min_age should me less than max_age.")
        return values


class UserProfile(BaseUserProfile):
    """Profile model."""

    id: uuid.UUID
    user_id: uuid.UUID
    subscriber: datetime | None


class UserProfileUpdate(BaseUserProfile):
    """Profile update model."""

    ...
