import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

AGE_MIN = 18
AGE_MAX = 99
RANGE_MIN = 0
RANGE_MAX = 999


class AuthUser(Base):
    __tablename__ = "auth_user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_delete: Mapped[bool] = mapped_column(default=False)

    questionnaire = relationship("UserQuestionnaire", back_populates="user")
    settings = relationship("UserSettings", back_populates="user")
    matches = relationship(
        "Match",
        primaryjoin="or_(AuthUser.id==Match.user1_id, AuthUser.id==Match.user2_id)",
        viewonly=True,
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subscriber: Mapped[datetime] = mapped_column(nullable=True)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    search_range_min: Mapped[Integer] = mapped_column(
        Integer,
        default=RANGE_MIN,
    )
    search_range_max: Mapped[Integer] = mapped_column(
        Integer,
        default=RANGE_MAX,
    )
    search_age_min: Mapped[Integer] = mapped_column(
        Integer,
        default=AGE_MIN,
    )
    search_age_max: Mapped[Integer] = mapped_column(
        Integer,
        default=AGE_MAX,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=True,
    )
    user = relationship("AuthUser", back_populates="settings")
