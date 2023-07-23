from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    number_of_likes: Mapped[int] = mapped_column(default=0)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False,
    )


class Rating(Base):
    __tablename__ = "rating"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete=("CASCADE")), primary_key=True,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete=("CASCADE")), primary_key=True,
    )
    like_is_toggeled: Mapped[bool | None] = mapped_column(default=None)
