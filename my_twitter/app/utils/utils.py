import asyncio
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Type
from urllib.parse import urljoin

import aiofiles
from app.database.models import User
from app.settings.classes import Settings
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload


class ImageManager:
    __ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]

    def __init__(
        self,
        settings: Settings,
        user: User,
        image: UploadFile,
    ):
        if image.content_type not in self.__ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Файл не является изображением или не поддерживается.",
            )
        self.__image = image
        if self.__image.filename is None:
            raise HTTPException(status_code=400, detail="У файла нет имени.")
        filename_list = self.__image.filename.split(".")
        if len(filename_list) < 2:
            raise HTTPException(status_code=400, detail="У файла нет расширения.")
        extension = filename_list[-1]
        filename = ".".join([str(uuid.uuid4()), extension])
        self.__file_path = os.path.join(
            settings.IMAGES_FOLDER_NAME, str(user.id), filename
        )
        self.__abs_file_path = settings.MEDIA_FOLDER_ROOT / self.__file_path

    async def save(self) -> None:
        """
        Функция сохраняет файл.

        :return: None.
        """
        await save_file(self.__abs_file_path, self.__image)

    @property
    def image(self) -> UploadFile:
        """
        Возвращает переданный файл.

        :return: UploadFile.
        """
        return self.__image

    @property
    def file_path(self) -> str:
        """
        Возвращает путь до файла относительно MEDIA_FOLDER_ROOT.

        :return: Относительный путь.
        """
        return self.__file_path

    @property
    def abs_file_path(self) -> Path:
        """
        Возвращает полный путь до файла.

        :return: Полный путь до файла
        """
        return self.__abs_file_path


def get_image_url(file_path: str, settings: Settings) -> str:
    """
    Функция возвращает url файла согласно настроек.

    :param file_path: Путь к файлу относительно MEDIA_FOLDER_ROOT.
    :param settings: Settings.
    :return: str
    """

    normalized_path = os.path.normpath(file_path).replace("\\", "/").strip("/")
    media_url = (
        settings.MEDIA_URL
        if settings.MEDIA_URL.endswith("/")
        else settings.MEDIA_URL + "/"
    )
    return urljoin(media_url, normalized_path)


async def save_file(file_path: Path, file: UploadFile) -> None:
    """
    Функция сохраняет файл по указанному пути.

    :param file_path: Путь сохранения.
    :param file: Файл.
    :return: None.
    """
    os.makedirs(file_path.parent.as_posix(), exist_ok=True)
    async with aiofiles.open(file_path, "wb") as buffer:
        while chunk := await file.read(1024):  # Читаем файл частями
            await buffer.write(chunk)  # Записываем в файл


async def get_or_create[T](
    session: AsyncSession, model: Type[T], data: Dict[str, Any]
) -> tuple[bool, T]:
    """
    Функция вернёт объект модели по заданным параметрам, если такой существует, в противном случае создаст его.

    :param session: AsyncSession.
    :param model: Модель базы данных.
    :param data: Данные модели.
    :return: (True, object) - если объект был создан, иначе (False, object)
    """
    obj_q = await session.execute(select(model).filter_by(**data))
    obj = obj_q.scalars().first()
    if obj:
        return False, obj
    new_obj = model(**data)
    session.add(new_obj)
    await session.commit()
    return True, new_obj


async def get_or_create_test_user(
    session: AsyncSession, settings: Settings
) -> tuple[bool, User]:
    """
    Функция возвращает тестового пользователя. Если он ещё не существует, то создаст его.

    :param session: AsyncSession.
    :param settings: Settings.
    :return: (True, User) - если объект был создан, иначе (False, User)
    """
    test_user = settings.TEST_USER
    return await get_or_create(
        session,
        User,
        dict(
            api_key=test_user.api_key,
            first_name=test_user.first_name,
            surname=test_user.surname,
            middle_name=test_user.middle_name,
        ),
    )


async def get_user_or_test_user(
    session: AsyncSession, settings: Settings, api_key: str
) -> User:
    """
    Вернёт пользователя с заданным api_key.
    Если такого пользователя нет, то вернёт тестового пользователя.

    :param session: AsyncSession.
    :param settings: Settings.
    :param api_key: Api_key пользователя.
    :return: User.
    """
    user_q = await session.execute(
        select(User)
        .where(User.api_key == api_key)
        .options(subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions))
    )
    user = user_q.scalars().one_or_none()
    if not user:
        user_q = await session.execute(
            select(User)
            .where(User.api_key == settings.TEST_USER.api_key)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
    return user


async def delete_img_file(*file_path: str, settings: Settings) -> None:
    """
    Функция удаляет файлы по переданным путям с учётом настроек.

    :param file_path: Путь к файлу.
    :param settings: Settings.
    :return: None.
    """
    tasks = [delete_file_async(settings.MEDIA_FOLDER_ROOT / path) for path in file_path]
    await asyncio.gather(*tasks)


async def delete_file_async(file_path: Path) -> None:
    """
    Функция удаляет файл по переданному пути.

    :param file_path: Путь к файлу.
    :return: None.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


async def get_user_with_apikey_and_user_with_id(
    session: AsyncSession, api_key: str, user_id: int, settings: Settings
) -> tuple[User, User]:
    """
    Функция вернёт 2 пользователей, одного текущего,
    по api-key (если такого нет, вернёт тестового пользователя из-за особенности фронта),
    второго по его id.

    :param session: AsyncSession.
    :param api_key: API key пользователя.
    :param user_id: ID пользователя.
    :param settings: Settings.
    :return: (API key пользователь, ID пользователь)
    """
    user_api = await get_user_or_test_user(session, settings, api_key)
    another_user_q = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions))
    )
    another_user = another_user_q.scalars().one()
    return user_api, another_user
