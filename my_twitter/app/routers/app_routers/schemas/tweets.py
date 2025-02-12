from typing import List, Optional, Self

from app.database.models.tweet import MAX_TWEET_LENGTH
from app.routers.app_routers.schemas.base import BaseSchema
from app.routers.app_routers.schemas.likes import LikesSchema
from app.routers.app_routers.schemas.medias import AttachmentSchema
from app.routers.app_routers.schemas.users import BaseUserSchema
from app.settings.classes import Settings
from app.utils.utils import get_image_url
from pydantic import BaseModel, Field, computed_field


class OutBaseTweet(BaseModel):
    """
    Базовая схема твита.
    """

    id: int

    class Config:
        from_attributes = True


class OutTweet(OutBaseTweet):
    """
    Полная схема твита.
    """

    settings: Optional[Settings] = Field(None, exclude=True)
    tweet_attachments: List[AttachmentSchema] = Field(exclude=True)
    content: str
    author: BaseUserSchema
    likes: List[LikesSchema]

    def set_settings(self, settings: Settings) -> Self:
        """
        Функция принимает файл настроек.
        (Для сериализации вложений необходим файл настроек.)

        :param settings: Settings.
        :return: None.
        """
        self.settings = settings
        return self

    @computed_field
    def attachments(self) -> List[str]:
        if self.settings is None:
            raise ValueError("Не задан файл настроек для сериализации вложений твита.")
        return [
            get_image_url(attachment.image_path, self.settings)
            for attachment in self.tweet_attachments
        ]


class InTweetSchema(BaseModel):
    """
    Класс-схема входящих данных, для создания твита.
    """

    tweet_data: str = Field(..., max_length=MAX_TWEET_LENGTH)
    tweet_media_ids: List[int]


class OutSimpleResponseTweet(BaseSchema):
    """
    Простая Out-схема твита.
    """

    tweet: OutBaseTweet = Field(exclude=True)

    @computed_field
    def tweet_id(self) -> int:
        """
        Возвращает id твита.
        :return: Id твита.
        """
        return self.tweet.id


class OutResponseTweet(BaseSchema):
    """
    Out-схема твита.
    """

    tweets: List[OutTweet]
