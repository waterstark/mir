import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import AuthUser
from src.database import Base


class Match(Base):
    __tablename__ = "match"
    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="_match_uc"),
        CheckConstraint("NOT(user1_id = user2_id)", name="_match_cc"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user1_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    user1 = relationship(
        "AuthUser",
        backref="matches_to",
        primaryjoin=AuthUser.id == user1_id,
    )
    user2_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    user2 = relationship(
        "AuthUser",
        backref="matches_from",
        primaryjoin=AuthUser.id == user2_id,
    )
