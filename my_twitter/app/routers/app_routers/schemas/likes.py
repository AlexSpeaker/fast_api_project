from app.routers.app_routers.schemas.users import BaseUserSchema
from pydantic import BaseModel, ConfigDict, Field, computed_field


class LikesSchema(BaseModel):
    """
    Схема лайков.
    """

    user: BaseUserSchema = Field(exclude=True)

    @computed_field
    def user_id(self) -> int:
        """
        Возвращает ID автора лайка.

        :return: ID автора лайка.
        """
        return self.user.id

    @computed_field
    def name(self) -> str:
        """
        Возвращает имя автора лайка.

        :return: Имя автора лайка.
        """
        return str(self.user.name)

    model_config = ConfigDict(from_attributes=True)
