from typing import TYPE_CHECKING, List

from app.database.models.base import Base
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.like import Like
    from app.database.models.subscriptions import Subscriptions
    from app.database.models.tweet import Tweet

MAX_NAME_LENGTH = 255
MAX_API_KEY_LENGTH = 255


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    surname: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=True)
    api_key: Mapped[str] = mapped_column(
        String(MAX_API_KEY_LENGTH), nullable=False, unique=True, index=True
    )

    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author")
    likes: Mapped[List["Like"]] = relationship(back_populates="user")

    my_subscriptions: Mapped[List["Subscriptions"]] = relationship(
        primaryjoin="User.id == Subscriptions.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    users_in_my_subscriptions: AssociationProxy[List["User"]] = association_proxy(
        "my_subscriptions",
        "follower",
        creator=lambda user_obj: Subscriptions(follower_id=user_obj.id),
    )

    my_subscribers: Mapped[List["Subscriptions"]] = relationship(
        primaryjoin="User.id == Subscriptions.follower_id",
        back_populates="follower",
    )
    users_following_me: AssociationProxy[List["User"]] = association_proxy(
        target_collection="my_subscribers", attr="user"
    )
