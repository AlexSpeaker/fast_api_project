import logging.config
import os
from typing import Any

from app.database.database import Database
from app.settings.classes import Settings
from fastapi import FastAPI


class CustomFastApi(FastAPI):
    """
    Расширенный FastAPI класс.
    """

    def __init__(
        self, *args: Any, settings: Settings, db: Database, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__settings = settings
        self.__db = db
        os.makedirs(settings.MEDIA_FOLDER_ROOT, exist_ok=True)
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)
        for (
            _,
            handler_config,
        ) in self.__settings.LOG_SETTINGS.LOGGING_CONFIG.get("handlers", {}).items():
            if "filename" in handler_config:
                log_dir = os.path.dirname(handler_config["filename"])
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)

        logging.config.dictConfig(self.__settings.LOG_SETTINGS.LOGGING_CONFIG)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Возвращает логер приложения.

        :param name: Имя логера.
        :return: Logger.
        """
        return logging.getLogger(".".join(["my_twitter_app", name]))

    def get_settings(self) -> Settings:
        """
        Возвращает подключенные настройки приложения.

        :return: Settings.
        """
        return self.__settings

    def get_db(self) -> Database:
        """
        Возвращает подключенный к приложению инструмент работы с БД.

        :return: Database.
        """
        return self.__db
