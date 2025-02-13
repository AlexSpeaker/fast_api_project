from datetime import datetime
from typing import TYPE_CHECKING, List

from app.database.models.base import Base
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

if TYPE_CHECKING:
    from app.database.models.attachment import Attachment
    from app.database.models.like import Like
    from app.database.models.user import User

MAX_TWEET_LENGTH = 5000


class Tweet(Base):
    __tablename__ = "tweets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(MAX_TWEET_LENGTH), nullable=False)
    created: Mapped[datetime] = mapped_column(
        default=datetime.now, server_default=func.now()
    )

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="selectin")
    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet", lazy="selectin", cascade="all, delete-orphan"
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        back_populates="tweet", lazy="selectin", cascade="all, delete-orphan"
    )

    @validates("content")
    def validate_content(self, _: str, value: str) -> str:
        if len(value) > MAX_TWEET_LENGTH:
            raise ValueError(
                f"Tweet content must be less than {MAX_TWEET_LENGTH} characters."
            )
        return value

    @property
    def tweet_attachments(self) -> List["Attachment"]:
        """
        Функция возвращает вложения.
        Необходимо из-за одинакового названия поля в модели и в схеме сериализации,
        но содержащую разную суть (в схеме это список из url).

        :return:  List[Attachment]
        """
        return self.attachments
