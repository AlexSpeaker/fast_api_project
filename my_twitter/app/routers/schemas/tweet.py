from typing import List, Sequence

from pydantic import BaseModel, Field, computed_field

from my_twitter.app.routers.schemas.like import UserLikeOutShort
from my_twitter.app.routers.schemas.user import UserOutShort


class TweetInSchema(BaseModel):
    tweet_data: str
    tweet_media_ids: List[int]


class TweetsResultOutSchema(BaseModel):
    result: bool


class TweetCreateOutSchema(BaseModel):
    id: int = Field(exclude=True)
    result: bool = True

    @computed_field
    def tweet_id(self) -> int:
        return self.id

    class ConfigDict:
        from_attributes = True


class TweetSchema(BaseModel):
    id: int
    content: str
    author: UserOutShort
    get_attachments_link: List[str] = Field(exclude=True)
    get_users_like: List[UserLikeOutShort] = Field(exclude=True)

    @computed_field
    def attachments(self) -> List[str]:
        return self.get_attachments_link

    @computed_field
    def likes(self) -> List[UserLikeOutShort]:
        return self.get_users_like

    class ConfigDict:
        from_attributes = True


class TweetsOutSchema(BaseModel):
    result: bool = True
    tweets: Sequence[TweetSchema]
