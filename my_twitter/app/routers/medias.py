from typing import Annotated

from fastapi import APIRouter, Depends, Request, UploadFile

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import Attachment
from my_twitter.app.routers.schemas.medias import MediaCreateOutSchema
from my_twitter.app.utils.api_key import api_key_validator
from my_twitter.app.utils.dependencies import GetDBDIRInfo
from my_twitter.app.utils.file_manager import file_manager, file_validation

router = APIRouter(
    tags=["media"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/medias",
    response_model=MediaCreateOutSchema,
    name="Create a media",
)
async def create_upload_file(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    file: UploadFile,
    request: Request,
):
    """Роут для записи медиа файлов."""
    db: DB = instance.get_db()
    dir_info: dict = instance.get_dir_info()

    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
        file_valid = file_validation(file)
        img_url = await file_manager(dir_info, user.login.key, file_valid)
        img = Attachment(image_url=img_url)

        session.add(img)
        await session.commit()
    return img
