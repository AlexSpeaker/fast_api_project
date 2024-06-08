import os
import time
from pathlib import Path
from typing import List

import aiofiles
from fastapi import HTTPException, UploadFile


async def file_manager(dir_info: dict, api_key: str, file: UploadFile) -> str:
    """Функция сохранит файл и вернёт url ссылку."""
    time_stamp = time.time()
    folder = api_key
    Path(os.path.join(dir_info["BASE_DIR_MEDIA"], folder)).mkdir(
        parents=True, exist_ok=True
    )
    file_name = "_".join([str(time_stamp).replace(".", "_"), str(file.filename)])
    path = os.path.join(dir_info["BASE_DIR_MEDIA"], folder, file_name)
    async with aiofiles.open(path, "wb") as file_media:
        content = await file.read()
        await file_media.write(content)
    return f"images/{folder}/{file_name}"


def file_validation(file: UploadFile) -> UploadFile:
    """Проверит, является ли файл картинкой и весит меньше 5МБ."""
    if file.size and file.size > 5242880:
        raise HTTPException(status_code=406, detail="The file is too big, max 5MB.")
    elif file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=406, detail="You are loading something wrong.")
    return file


async def cleaner(files_path: List[str], dir_info: dict):
    """Функция удалит файлы по относительным путям в списке."""
    for path in files_path:
        url, user, img = path.split('/')
        os.remove(os.path.join(dir_info["BASE_DIR_MEDIA"], user, img))
