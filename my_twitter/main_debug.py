import uvicorn
from app.application.factory_function import get_app
from app.database.database import Database
from app.settings.classes import DBSettings, Settings
from main import app

db_settings_debug = DBSettings(
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/twitter_db"
)
settings_debug = Settings(
    BASE_DIR=app.get_settings().BASE_DIR,
    IMAGES_FOLDER_NAME=app.get_settings().IMAGES_FOLDER_NAME,
    MEDIA_FOLDER_ROOT=app.get_settings().MEDIA_FOLDER_ROOT,
    MEDIA_URL=app.get_settings().MEDIA_URL,
    STATIC_ROOT=app.get_settings().STATIC_ROOT,
    STATIC_URL=app.get_settings().STATIC_URL,
    DB_SETTINGS=db_settings_debug,
    DEBUG=True,
    LOG_SETTINGS=app.get_settings().LOG_SETTINGS,
)
db_debug = Database(db_url=settings_debug.DB_SETTINGS.DATABASE_URL)
app_debug = get_app(settings=settings_debug, db=db_debug)

if __name__ == "__main__":
    uvicorn.run(app_debug, host="127.0.0.1", port=8000)
