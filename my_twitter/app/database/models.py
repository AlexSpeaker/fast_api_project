from datetime import datetime
from typing import Any, List

from sqlalchemy import VARCHAR, ForeignKey, UniqueConstraint, func
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship, validates

Base: Any = declarative_base()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    surname: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    middle_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)

    login: Mapped["ApiKey"] = relationship(back_populates="user")
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
        creator=lambda user_obj: Subscriptions(follower=user_obj),
    )
    # Мои подписчики.
    my_subscribers: Mapped[List["Subscriptions"]] = relationship(
        primaryjoin="User.id == Subscriptions.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    users_following_me: AssociationProxy[List["User"]] = association_proxy(
        target_collection="my_subscribers", attr="user"
    )


class Subscriptions(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "follower_id", name="user_id_follower_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(column="user.id"), nullable=False)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey(column="user.id"), nullable=False
    )

    follower: Mapped[User] = relationship(
        foreign_keys=[follower_id], back_populates="my_subscribers", lazy="joined"
    )
    user: Mapped[User] = relationship(
        foreign_keys=[user_id], back_populates="my_subscriptions", lazy="joined"
    )

    @validates("follower_id")
    def validate_follower_id(self, key, value):
        if value == self.user.id:
            raise ValueError(f"You can't follow yourself. follower_id={value} user_id={self.user.id}")
        return value


class ApiKey(Base):
    __tablename__ = "api_key"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    key: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
    banned: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="login", lazy="joined")


class Tweet(Base):
    __tablename__ = "tweet"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(VARCHAR(50000), nullable=False)
    created: Mapped[datetime] = mapped_column(
        default=datetime.now, server_default=func.now()
    )

    author: Mapped[User] = relationship(back_populates="tweets", lazy="selectin")
    likes: Mapped[List["Like"]] = relationship(back_populates="tweet", lazy="selectin")
    attachments: Mapped[List["Attachment"]] = relationship(
        back_populates="tweet", lazy="selectin"
    )

    @hybrid_property
    def get_attachments_link(self) -> List[str]:
        return [attachment.image_url for attachment in self.attachments]

    @hybrid_property
    def get_users_like(self) -> List[User]:
        return [like.user for like in self.likes]


class Like(Base):
    __tablename__ = "like"
    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="tweet_id_user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweet.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped[User] = relationship(lazy="selectin")
    tweet: Mapped[Tweet] = relationship()


class Attachment(Base):
    __tablename__ = "attachment"
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweet.id", ondelete="CASCADE"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    tweet: Mapped[Tweet] = relationship()
