import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Numeric,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from src.auth.models import AuthUser
from src.database import Base
from src.questionnaire.params_choice import AlcoholType, Gender, Goal, SmokingType, SportType


class BlackListUser(Base):
    __tablename__ = "black_list_user"
    __table_args__ = (
        UniqueConstraint("blocked_by_id", "blocked_id", name="_black_list_uc"),
        CheckConstraint("NOT(blocked_by_id = blocked_id)", name="_black_list_cc"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    blocked_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    blocked_by = relationship(
        "AuthUser",
        backref="blocked_list",
        primaryjoin=AuthUser.id == blocked_by_id,
    )
    blocked_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    blocked = relationship(
        "AuthUser",
        backref="blocked_by_list",
        primaryjoin=AuthUser.id == blocked_id,
    )


user_hobby = Table(
    "user_hobby",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user_questionnaire.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "hobby_id",
        ForeignKey("user_questionnaire_hobby.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class UserQuestionnaire(Base):
    __tablename__ = "user_questionnaire"
    __table_args__ = (
        UniqueConstraint("user_id", name="_user_id_uc"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )
    is_prem: Mapped[bool] = mapped_column(default=False, nullable=False)
    rate: Mapped[float] = mapped_column(default=1000, nullable=True)
    quest_lists_per_day: Mapped[int] = mapped_column(default=0, nullable=False)
    firstname: Mapped[str] = mapped_column(String(length=256), nullable=True)
    lastname: Mapped[str] = mapped_column(String(length=256), nullable=True)
    gender: Mapped[str] = mapped_column(ChoiceType(Gender), nullable=True)
    photo: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    city: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    latitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    longitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    about: Mapped[str] = mapped_column(String, nullable=True)
    height: Mapped[int] = mapped_column(nullable=True)
    goals: Mapped[str] = mapped_column(ChoiceType(Goal), nullable=True)
    sport: Mapped[str] = mapped_column(ChoiceType(SportType), nullable=False)
    smoking: Mapped[str] = mapped_column(ChoiceType(SmokingType), nullable=False)
    alcohol: Mapped[str] = mapped_column(ChoiceType(AlcoholType), nullable=False)
    is_visible: Mapped[bool] = mapped_column(default=True, nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=False)
    hobbies: Mapped[list["UserQuestionnaireHobby"]] = relationship(
        secondary=user_hobby,
        lazy="selectin",
        cascade="all,delete-orphan",
        single_parent=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    user = relationship("AuthUser", back_populates="questionnaire")


class UserQuestionnaireHobby(Base):
    __tablename__ = "user_questionnaire_hobby"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    hobby_name: Mapped[str] = mapped_column(String(length=256), nullable=False)
