from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DBSettings:
    DATABASE_URL: str


@dataclass(frozen=True)
class Settings:
    BASE_DIR: Path
    IMAGES_FOLDER_NAME: str
    MEDIA_FOLDER_NAME: str
    STATIC_ROOT: Path
    STATIC_URL: str
    DB_SETTINGS: DBSettings
    DEBUG: bool
