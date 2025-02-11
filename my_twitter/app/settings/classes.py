from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class DBSettings:
    DATABASE_URL: str


@dataclass(frozen=True)
class TestUserData:
    api_key = "test"
    first_name = "Александр"
    surname = "Тестов"
    middle_name = "Петрович"


@dataclass(frozen=True)
class Settings:
    BASE_DIR: Path
    MEDIA_FOLDER_ROOT: Path
    MEDIA_URL: str
    IMAGES_FOLDER_NAME: str
    STATIC_ROOT: Path
    STATIC_URL: str
    DB_SETTINGS: DBSettings
    DEBUG: bool
    LOG_SETTINGS: "LogerSettings"
    TEST_USER: TestUserData = TestUserData()


@dataclass(frozen=True)
class LogerSettings:
    LOGGING_CONFIG: Dict[str, Any]
