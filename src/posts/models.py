import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import AuthUser
from src.database import Base


class Message(Base):
    __tablename__ = "message"
    __table_args__ = (
        CheckConstraint("NOT(sender_id = receiver_id)", name="_message_cc"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    message_text: Mapped[str] = mapped_column(String)

    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    sended = relationship(
        "AuthUser",
        backref="sended_messages",
        primaryjoin=AuthUser.id == sender_id,
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
    )
    receiver = relationship(
        "AuthUser",
        backref="messages_received",
        primaryjoin=AuthUser.id == receiver_id,
    )
