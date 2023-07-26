from datetime import datetime
from sqlalchemy_utils import ChoiceType
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.auth.params_choice import for_gender, for_goals, for_body_type, for_passion
from src.database import Base
from sqlalchemy import Numeric


class AuthUser(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=50), unique=True, index=True, nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)


class UserSettings(Base):
    __tablename__ = 'user_settings'

    id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    black_list: Mapped[int] = mapped_column(default=False, nullable=True)
    subscriber: Mapped[datetime] = mapped_column(nullable=True)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserQuestionnaire(Base):
    __tablename__ = 'user_questionnaire'

    id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    firstname: Mapped[str] = mapped_column(String(length=15), nullable=False)
    lastname: Mapped[str] = mapped_column(String(length=15), nullable=True)
    gender: Mapped[str] = mapped_column(ChoiceType(choices=for_gender))
    photo: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str]  # апи + live search
    city: Mapped[str]  # апи + live search
    latitude: Mapped[Numeric] = mapped_column(Numeric(8, 5))
    longitude: Mapped[Numeric] = mapped_column(Numeric(8, 5))
    about: Mapped[str] = mapped_column(String)
    passion: Mapped[str] = mapped_column(ChoiceType(choices=for_passion))
    height: Mapped[int]
    goals: Mapped[str] = mapped_column(ChoiceType(choices=for_goals))
    body_type: Mapped[str] = mapped_column(ChoiceType(choices=for_body_type))
    is_visible: Mapped[bool] = mapped_column(default=True, nullable=False)
