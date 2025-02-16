from typing import Annotated

from app.database.database import Database
from app.database.models import Attachment
from app.routers.app_routers.schemas.medias import (
    BaseAttachmentSchema,
    OutAttachmentSchema,
)
from app.settings.classes import Settings
from app.utils.utils import (
    ImageManager,
    get_database,
    get_settings,
    get_user_or_test_user,
)
from fastapi import APIRouter, Depends, File, Header, UploadFile

router = APIRouter(tags=["media"])


@router.post(
    "/medias",
    response_model=OutAttachmentSchema,
    name="Загрузка изображений.",
    description="Загрузит и сохранит изображение текущего пользователя "
    "(по умолчанию тестовый пользователь) согласно настройкам.",
)
async def create_upload_file(
    file: Annotated[UploadFile, File(..., media_type="image/*")],
    db: Annotated[Database, Depends(get_database)],
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str, Header(...)] = "test",
) -> OutAttachmentSchema:
    """
    Загрузит и сохранит изображение текущего пользователя (по умолчанию тестовый пользователь) согласно настройкам.

    :param file: Объект с изображением.
    :param db: Инструмент работы с БД.
    :param settings: Настройки приложения.
    :param api_key: API key пользователя.
    :return: OutAttachmentSchema.
    """
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, settings, api_key)
        attachment_manager = ImageManager(settings, user, file)
        await attachment_manager.save()
        attachment = Attachment(image_path=attachment_manager.file_path)
        session.add(attachment)
        await session.commit()
    return OutAttachmentSchema(media=BaseAttachmentSchema.model_validate(attachment))
