from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DB:
    def __init__(
        self,
        database_url: str,
        create_async_engine_kwargs: Optional[dict] = None,
        async_sessionmaker_kwargs: Optional[dict] = None,
    ) -> None:
        self._database_url = database_url
        self._engine = (
            create_async_engine(database_url, **create_async_engine_kwargs)
            if create_async_engine_kwargs
            else create_async_engine(database_url)
        )
        self._async_session = (
            async_sessionmaker(
                self._engine, expire_on_commit=False, **async_sessionmaker_kwargs
            )
            if async_sessionmaker_kwargs
            else async_sessionmaker(self._engine, expire_on_commit=False)
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def get_session(self) -> AsyncSession:
        return self._async_session()

    def __repr__(self):
        return f"<DB: {self._database_url}>"
