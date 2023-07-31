import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import ChoiceType

from src.auth.params_choice import for_body_type, for_gender, for_goals, for_passion
from src.database import Base


class AuthUser(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "auth_user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(length=50), unique=True, index=True, nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_delete: Mapped[bool] = mapped_column(default=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True)
    subscriber: Mapped[datetime] = mapped_column(nullable=True)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class BlackListUser(Base):
    __tablename__ = "black_list_user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"))
    blocked_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"))
    idx_user_to_block = Index("idx_user_to_block", user_id, blocked_id, unique=True)


class UserQuestionnaire(Base):
    __tablename__ = "user_questionnaire"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True)
    firstname: Mapped[str] = mapped_column(String(length=256), nullable=False)
    lastname: Mapped[str] = mapped_column(String(length=256), nullable=True)
    gender: Mapped[str] = mapped_column(ChoiceType(choices=for_gender), nullable=True)
    photo: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    city: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    latitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    longitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    about: Mapped[str] = mapped_column(String, nullable=True)
    passion: Mapped[str] = mapped_column(ChoiceType(choices=for_passion), nullable=True)
    height: Mapped[int] = mapped_column(nullable=True)
    goals: Mapped[str] = mapped_column(ChoiceType(choices=for_goals), nullable=True)
    body_type: Mapped[str] = mapped_column(ChoiceType(choices=for_body_type), nullable=True)
    is_visible: Mapped[bool] = mapped_column(default=True, nullable=False)
