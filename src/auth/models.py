import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AuthUser(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "auth_user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(length=50), unique=True, index=True, nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_delete: Mapped[bool] = mapped_column(default=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True)
    subscriber: Mapped[datetime] = mapped_column(nullable=True)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)
