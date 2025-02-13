from typing import List

from app.routers.app_routers.schemas.base import BaseSchema
from pydantic import BaseModel, Field, computed_field, ConfigDict


class BaseUserSchema(BaseModel):
    """
    Базовая схема пользователя.
    """

    id: int
    first_name: str = Field(exclude=True)
    middle_name: str | None = Field(exclude=True)
    surname: str = Field(exclude=True)

    @computed_field
    def name(self) -> str:
        """
        Возвращает полное имя.
        :return: Полное имя
        """
        return " ".join(
            [name for name in [self.first_name, self.middle_name, self.surname] if name]
        )

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseUserSchema):
    """
    Полная схема пользователя.
    """

    users_in_my_subscriptions: List[BaseUserSchema] = Field(exclude=True)
    users_following_me: List[BaseUserSchema] = Field(exclude=True)

    @computed_field
    def following(self) -> List[BaseUserSchema]:
        """
        Возвращает список из подписок пользователя.

        :return: Список из подписок пользователя.
        """
        return self.users_in_my_subscriptions

    @computed_field
    def followers(self) -> List[BaseUserSchema]:
        """
        Возвращает список из подписчиков на пользователя.

        :return: Список из подписчиков на пользователя.
        """
        return self.users_following_me

    model_config = ConfigDict(from_attributes=True)

class OutUserSchema(BaseSchema):
    """
    Out-схема пользователя
    """

    user: UserSchema
