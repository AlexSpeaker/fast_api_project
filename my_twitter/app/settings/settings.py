from pathlib import Path

from app.settings.classes import DBSettings, Settings

db_settings = DBSettings(
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/twitter_db"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

settings = Settings(
    BASE_DIR=BASE_DIR,
    IMAGES_FOLDER_NAME="images",
    MEDIA_FOLDER_NAME="media",
    STATIC_ROOT=BASE_DIR / "app" / "routers" / "static",
    STATIC_URL="/",
    DB_SETTINGS=db_settings,
    DEBUG=True,
)
