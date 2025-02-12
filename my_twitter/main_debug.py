import uvicorn
from app.application.factory_function import get_app
from app.database.database import Database
from app.settings.classes import DBSettings, Settings
from app.settings.settings import settings

db_settings_debug = DBSettings(
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/twitter_db"
)
settings_debug = Settings(
    BASE_DIR=settings.BASE_DIR,
    IMAGES_FOLDER_NAME=settings.IMAGES_FOLDER_NAME,
    MEDIA_FOLDER_ROOT=settings.MEDIA_FOLDER_ROOT,
    MEDIA_URL=settings.MEDIA_URL,
    STATIC_ROOT=settings.STATIC_ROOT,
    STATIC_URL=settings.STATIC_URL,
    DB_SETTINGS=db_settings_debug,
    DEBUG=True,
    LOG_SETTINGS=settings.LOG_SETTINGS,
)
db_debug = Database(db_url=settings_debug.DB_SETTINGS.DATABASE_URL)
app_debug = get_app(settings=settings_debug, db=db_debug)

if __name__ == "__main__":
    uvicorn.run(app_debug, host="127.0.0.1", port=8000)
