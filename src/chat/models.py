import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import ChoiceType

from src.chat.util import MessageStatus
from src.database import Base


class Message(Base):
    __tablename__ = "message"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("match.id", ondelete="RESTRICT"),
        nullable=False,
    )
    from_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    to_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(String(length=4096), nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )
    status: Mapped[MessageStatus] = mapped_column(
        ChoiceType(MessageStatus),
        default=MessageStatus.SENT,
        nullable=False,
    )
    captions: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
