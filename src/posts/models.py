from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Matches(Base):
    __tablename__ = "matches"

    match_id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False,
    )
    user1_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
    )
    user2_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )


class Likes(Base):
    __tablename__ = "likes"

    like_id: Mapped[int] = mapped_column(
        primary_key=True, index=True, nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), primary_key=True,
    )
    liked_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Messages(Base):
    __tablename__ = "messages"

    message_id: Mapped[int] = mapped_column(
        primary_key=True, index=True, nullable=False,
    )
    sender: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
    )
    receiver: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    message_text: Mapped[str] = mapped_column(String)
