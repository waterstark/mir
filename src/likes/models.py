import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import AuthUser
from src.database import Base


class UserLike(Base):
    __tablename__ = "user_like"
    __table_args__ = (
        UniqueConstraint("liker_id", "liking_id", name="_user_like_uc"),
        CheckConstraint("NOT(liker_id = liking_id)", name="_user_like_cc"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    liker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"))
    liker = relationship("AuthUser", backref="likes_to", primaryjoin=AuthUser.id==liker_id)
    liking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"))
    liking = relationship("AuthUser", backref="likes_from", primaryjoin=AuthUser.id==liking_id)
