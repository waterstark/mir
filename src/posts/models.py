import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Match(Base):
    __tablename__ = "match"

    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False,
    )
    user1_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="RESTRICT"),
    )
    user2_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="RESTRICT"),
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True,
    )
    sender: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id"),
    )
    receiver: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id"),
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    message_text: Mapped[str] = mapped_column(String)
