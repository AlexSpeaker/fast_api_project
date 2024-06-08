import os
from pathlib import Path

DEBUG = not os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR_STATIC = os.path.join(BASE_DIR, "static")


NAME_FOLDER_MEDIA: str = "images_debug" if DEBUG else "images"

BASE_DIR_MEDIA: str = os.path.join(BASE_DIR_STATIC, NAME_FOLDER_MEDIA)
Path(BASE_DIR_MEDIA).mkdir(parents=True, exist_ok=True)
DIR_INFO = dict(
    BASE_DIR=BASE_DIR,
    BASE_DIR_STATIC=BASE_DIR_STATIC,
    NAME_FOLDER_MEDIA=NAME_FOLDER_MEDIA,
    BASE_DIR_MEDIA=BASE_DIR_MEDIA,
)

if DEBUG:
    # База данных DEBUG
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/twitter_db"
else:
    # База данных Docker
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@database:5432/twitter_db"
