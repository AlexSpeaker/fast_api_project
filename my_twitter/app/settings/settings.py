from pathlib import Path

from app.settings.classes import DBSettings, LogerSettings, Settings

db_settings = DBSettings(
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@database:5432/twitter_db"
)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [line: %(lineno)d]",
            "datefmt": "%d.%m.%Y %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",  # Имя файла для логов
            "maxBytes": 1 * 1024 * 1024,  # Максимальный размер файла 1 MB
            "backupCount": 5,  # Количество резервных файлов
            "formatter": "default",
            "level": "DEBUG",  # Уровень логирования для файла
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",  # Уровень логирования для консоли
        },
    },
    "loggers": {
        "my_twitter_app": {
            "handlers": ["file", "console"],  # Обработчики для логгера
            "level": "DEBUG",  # Уровень логирования для логгера
            "propagate": False,  # Не передавать логи родительским логгерам
        },
    },
}

log_settings = LogerSettings(
    LOGGING_CONFIG=LOGGING_CONFIG,
)


settings = Settings(
    BASE_DIR=BASE_DIR,
    IMAGES_FOLDER_NAME="images",
    MEDIA_FOLDER_ROOT=BASE_DIR / "app" / "routers" / "media",
    MEDIA_URL="/media",
    STATIC_ROOT=BASE_DIR / "app" / "routers" / "static",
    STATIC_URL="/",
    DB_SETTINGS=db_settings,
    DEBUG=False,
    LOG_SETTINGS=log_settings,
)
