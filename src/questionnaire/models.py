import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from src.auth.models import AuthUser
from src.database import Base
from src.questionnaire.params_choice import BodyType, Gender, Goal, Passion


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


class UserQuestionnaire(Base):
    __tablename__ = "user_questionnaire"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    firstname: Mapped[str] = mapped_column(String(length=256), nullable=True)
    lastname: Mapped[str] = mapped_column(String(length=256), nullable=True)
    gender: Mapped[str] = mapped_column(ChoiceType(Gender), nullable=True)
    photo: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    city: Mapped[str] = mapped_column(String, nullable=True)  # апи + live search
    latitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    longitude: Mapped[Numeric] = mapped_column(Numeric(8, 5), nullable=True)
    about: Mapped[str] = mapped_column(String, nullable=True)
    passion: Mapped[str] = mapped_column(ChoiceType(Passion), nullable=True)
    height: Mapped[int] = mapped_column(nullable=True)
    goals: Mapped[str] = mapped_column(ChoiceType(Goal), nullable=True)
    body_type: Mapped[str] = mapped_column(ChoiceType(BodyType), nullable=True)
    is_visible: Mapped[bool] = mapped_column(default=True, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=True,
    )
    user = relationship("AuthUser", back_populates="questionnaire")
