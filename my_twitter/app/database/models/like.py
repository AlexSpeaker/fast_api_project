from typing import TYPE_CHECKING

from app.database.models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.tweet import Tweet
    from app.database.models.user import User


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="tweet_id_user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweets.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")
