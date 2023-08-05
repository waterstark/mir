import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserLike(Base):
    __tablename__ = "user_like"

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id"),
    )
    liked_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id"),
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
