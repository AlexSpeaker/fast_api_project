from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from app.application.classes import CustomFastApi
from app.application.factory_function import get_app
from app.database.database import Database
from app.settings.classes import DBSettings, Settings
from httpx import ASGITransport, AsyncClient
from tests.utils import create_db, create_users, drop_db


@pytest_asyncio.fixture
async def settings() -> Settings:
    db_settings = DBSettings(DATABASE_URL="sqlite+aiosqlite://")
    # db_settings = DBSettings(
    #     DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/twitter_db"
    # )

    base_dir = Path(__file__).resolve().parent

    return Settings(
        BASE_DIR=base_dir,
        IMAGES_FOLDER_NAME="images",
        MEDIA_FOLDER_NAME="media",
        STATIC_ROOT=base_dir / "temp" / "static",
        STATIC_URL="/",
        DB_SETTINGS=db_settings,
        DEBUG=False,
    )


@pytest_asyncio.fixture
async def app(settings: Settings, db: Database) -> CustomFastApi:
    return get_app(settings=settings, db=db)


@pytest_asyncio.fixture
async def db(settings: Settings) -> AsyncGenerator[Database, None]:
    db = Database(settings.DB_SETTINGS.DATABASE_URL)
    await create_db(db=db)
    await create_users(db=db)
    yield db
    await drop_db(db=db)


@pytest_asyncio.fixture
async def client(app: CustomFastApi) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
