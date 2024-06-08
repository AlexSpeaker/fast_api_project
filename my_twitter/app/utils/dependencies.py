from typing import Optional

from my_twitter.app.database.database import DB
from my_twitter.app.errors import AppError


class GetDBDIRInfo:
    """
    Класс хранит в себе информацию о подключённой БД
    и информацию о подключённой папке static.
    """

    db: Optional[DB] = None
    dir_info: Optional[dict] = None

    def get_db(self) -> DB:
        if self.db is None:
            raise AppError("No database found")
        return self.db

    def get_dir_info(self) -> dict:
        if self.dir_info is None:
            raise AppError("No media info found")
        return self.dir_info
