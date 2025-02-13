import shutil
from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from app.application.classes import CustomFastApi
from app.application.factory_function import get_app
from app.database.database import Database
from app.settings.classes import DBSettings, Settings
from app.settings.settings import log_settings
from httpx import ASGITransport, AsyncClient
from tests.utils import create_db, create_users, drop_db


@pytest_asyncio.fixture
async def settings() -> Settings:
    """
    Подготавливаем настройки для тестирования приложения.

    :return: Settings.
    """
    db_settings = DBSettings(DATABASE_URL="sqlite+aiosqlite://")

    base_dir = Path(__file__).resolve().parent

    return Settings(
        BASE_DIR=base_dir,
        IMAGES_FOLDER_NAME="images",
        MEDIA_FOLDER_ROOT=base_dir / "temp" / "media",
        MEDIA_URL="/media",
        STATIC_ROOT=base_dir / "temp" / "static",
        STATIC_URL="/",
        DB_SETTINGS=db_settings,
        DEBUG=False,
        LOG_SETTINGS=log_settings,
    )


@pytest_asyncio.fixture
async def app(settings: Settings, db: Database) -> CustomFastApi:
    """
    Создаём приложение для тестирования.

    :param settings: Settings.
    :param db: Database.
    :return: CustomFastApi.
    """
    return get_app(settings=settings, db=db)


@pytest_asyncio.fixture
async def db(settings: Settings) -> AsyncGenerator[Database, None]:
    """
    Создаём инструмент для работы с БД.
    Перед использованием создаём таблицы и заполняем минимальными данными.
    После использования - дропаем БД.

    :param settings: Settings.
    :return: AsyncGenerator[Database, None].
    """
    db = Database(settings.DB_SETTINGS.DATABASE_URL)
    await create_db(db=db)
    await create_users(db=db)
    yield db
    await drop_db(db=db)
    shutil.rmtree(folder_path)


@pytest_asyncio.fixture
async def client(app: CustomFastApi) -> AsyncClient:
    """
    Фикстура для создания асинхронного тестового клиента.

    :param app: CustomFastApi.
    :return: AsyncClient.
    """
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest_asyncio.fixture
async def fake_image() -> dict[str, tuple[str, bytes, str]]:
    """
    Фикстура для создания тестового изображения.

    :return: dict[str, tuple[str, bytes, str]].
    """
    return {"file": ("test_image.png", b"fake_image_data", "image/png")}
