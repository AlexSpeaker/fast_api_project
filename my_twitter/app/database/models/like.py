from typing import TYPE_CHECKING

from app.database.models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.tweet import Tweet
    from app.database.models.user import User


class Like(Base):
    """
    Лайк твита.

    **id** ID лайка. \n
    **tweet_id** ID твита. \n
    **user_id** ID пользователя. \n
    **user** Связанный пользователь. \n
    **tweet** Связанный твит.
    """
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="tweet_id_user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweets.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="likes", lazy="selectin")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")
