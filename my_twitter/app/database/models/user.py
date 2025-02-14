from typing import TYPE_CHECKING, List

from app.database.models.base import Base
from app.database.models.subscriptions import Subscriptions
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.database.models.like import Like
    from app.database.models.tweet import Tweet

MAX_NAME_LENGTH = 255
MAX_API_KEY_LENGTH = 255


class User(Base):
    """
    Пользователь.

    **id** ID пользователя. \n
    **first_name** Имя пользователя. \n
    **surname** Фамилия пользователя. \n
    **middle_name** Отчество пользователя. \n
    **api_key** Api-key пользователя. \n
    **tweets** Связанные твиты пользователя. \n
    **likes** Связанные лайки пользователя. \n
    **users_in_my_subscriptions** Подписки пользователя. \n
    **users_following_me** Подписчики пользователя. \n
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    surname: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=True)
    api_key: Mapped[str] = mapped_column(
        String(MAX_API_KEY_LENGTH), nullable=False, unique=True, index=True
    )

    tweets: Mapped[List["Tweet"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    my_subscriptions: Mapped[List["Subscriptions"]] = relationship(
        primaryjoin="User.id == Subscriptions.user_id",
        cascade="all, delete-orphan",
    )
    users_in_my_subscriptions: AssociationProxy[List["User"]] = association_proxy(
        "my_subscriptions",
        "follower",
        creator=lambda user_obj: Subscriptions(follower_id=user_obj.id),
    )

    my_subscribers: Mapped[List["Subscriptions"]] = relationship(
        primaryjoin="User.id == Subscriptions.follower_id",
    )
    users_following_me: AssociationProxy[List["User"]] = association_proxy(
        target_collection="my_subscribers", attr="user"
    )
