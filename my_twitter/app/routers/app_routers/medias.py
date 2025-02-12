from typing import Annotated

from app.application.classes import CustomFastApi
from app.database.models import Attachment, User
from app.routers.app_routers.schemas.medias import (
    BaseAttachmentSchema,
    OutAttachmentSchema,
)
from app.utils.utils import ImageManager
from fastapi import APIRouter, File, Header, Request, UploadFile
from sqlalchemy import select

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
    request: Request,
    api_key: Annotated[str, Header(...)] = "test",
) -> OutAttachmentSchema:
    """
    Загрузит и сохранит изображение текущего пользователя (по умолчанию тестовый пользователь) согласно настройкам.

    :param file: Объект с изображением.
    :param request: Request.
    :param api_key: API key пользователя.
    :return:
    """
    app: CustomFastApi = request.app
    db = app.get_db()

    async with db.get_sessionmaker() as session:
        user_q = await session.execute(select(User).where(User.api_key == api_key))
        user = user_q.scalars().one()
        attachment_manager = ImageManager(app.get_settings(), user, file)
        await attachment_manager.save()
        attachment = Attachment(image_path=attachment_manager.file_path)
        session.add(attachment)
        await session.commit()
    return OutAttachmentSchema(media=BaseAttachmentSchema.model_validate(attachment))
