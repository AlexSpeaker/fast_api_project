import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class DBSettings:
    """
    Класс настроек DB.
    """

    DATABASE_URL: str


@dataclass(frozen=True)
class TestUserData:
    """
    Данные о тестовом пользователе.
    """

    api_key = "test"
    first_name = "Александр"
    surname = "Тестов"
    middle_name = "Петрович"


@dataclass(frozen=True)
class Settings:
    """
    Общий класс настроек.
    """

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

    def makedirs_MEDIA_FOLDER_ROOT(self) -> None:
        """
        Создаёт путь к MEDIA_FOLDER_ROOT.
        """
        os.makedirs(self.MEDIA_FOLDER_ROOT, exist_ok=True)

    def makedirs_STATIC_ROOT(self) -> None:
        """
        Создаёт путь к STATIC_ROOT.
        """
        os.makedirs(self.STATIC_ROOT, exist_ok=True)

    def makedirs_LOGGING_ROOT(self) -> None:
        """
        Создаёт путь к LOGS.
        """
        for (
            _,
            handler_config,
        ) in self.LOG_SETTINGS.LOGGING_CONFIG.get("handlers", {}).items():
            if "filename" in handler_config:
                log_dir = os.path.dirname(handler_config["filename"])
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)


@dataclass(frozen=True)
class LogerSettings:
    """
    Класс настроек LOGER.
    """

    LOGGING_CONFIG: Dict[str, Any]
