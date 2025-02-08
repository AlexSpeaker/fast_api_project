from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DBSettings:
    DATABASE_URL: str


@dataclass(frozen=True)
class Settings:
    BASE_DIR: Path
    MEDIA_ROOT: Path
    STATIC_ROOT: Path
    DB_SETTINGS: DBSettings
    DEBUG: bool
