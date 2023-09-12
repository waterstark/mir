import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import AuthUser
from src.database import Base


class UserLike(Base):
    __tablename__ = "user_like"
    __table_args__ = (
        UniqueConstraint("user_id", "liked_user_id", name="_user_like_uc"),
        CheckConstraint("NOT(user_id = liked_user_id)", name="_user_like_cc"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    user = relationship(
        "AuthUser",
        backref="likes_to",
        primaryjoin=AuthUser.id == user_id,
    )
    liked_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    liked_user = relationship(
        "AuthUser",
        backref="likes_from",
        primaryjoin=AuthUser.id == liked_user_id,
    )
    is_like: Mapped[bool] = mapped_column(
        Boolean,
        doc="Like or Skip"
    )
