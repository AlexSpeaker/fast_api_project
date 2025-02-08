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

    async def get_async_session(self) -> async_sessionmaker[AsyncSession]:
        return self.__async_sessionmaker
