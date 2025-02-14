from app.routers.app_routers.schemas.base import BaseSchema
from pydantic import BaseModel, ConfigDict, Field, computed_field


class BaseAttachmentSchema(BaseModel):
    """
    Базовая схема вложения.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class AttachmentSchema(BaseAttachmentSchema):
    """
    Схема вложения.
    """

    image_path: str


class OutAttachmentSchema(BaseSchema):
    """
    Out-схема вложения.
    """

    media: BaseAttachmentSchema = Field(exclude=True)

    @computed_field
    def media_id(self) -> int:
        """
        Возвращает id вложения.

        :return: Id вложения.
        """
        return self.media.id
