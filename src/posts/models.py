from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Match(Base):
    __tablename__ = "match"

    id: Mapped[int] = mapped_column(
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


class Like(Base):
    __tablename__ = "like"

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), primary_key=True,
    )
    liked_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
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
