from app.settings.settings import settings as app_settings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, db_url: str) -> None:
        self.__engine = create_async_engine(db_url)
        self.__async_sessionmaker = async_sessionmaker(
            self.__engine, expire_on_commit=False
        )

    def get_engine(self) -> AsyncEngine:
        return self.__engine

    @property
    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self.__async_sessionmaker


db = Database(db_url=app_settings.DB_SETTINGS.DATABASE_URL)
