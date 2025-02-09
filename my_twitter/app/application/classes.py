from typing import Any

from app.database.database import Database
from app.settings.classes import Settings
from fastapi import FastAPI


class CustomFastApi(FastAPI):

    def __init__(
        self, *args: Any, settings: Settings, db: Database, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__settings = settings
        self.__db = db

    def get_settings(self) -> Settings:
        return self.__settings

    def get_db(self) -> Database:
        return self.__db
