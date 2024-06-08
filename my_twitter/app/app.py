import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from my_twitter.app.database.database import DB
from my_twitter.app.routers.medias import router as media_router
from my_twitter.app.routers.static_html import router as static_html_router
from my_twitter.app.routers.tweets import router as tweets_router
from my_twitter.app.routers.users import router as users_router
from my_twitter.app.utils.dependencies import GetDBDIRInfo
from my_twitter.app.utils.exception_handler import unicorn_exception_handler
from my_twitter.app.utils.lifespan import lifespan
from my_twitter.settings import DIR_INFO


class AppCreator:

    def __init__(self, db: DB, dir_info: dict = DIR_INFO, **kwargs) -> None:
        self._dir_info = dir_info
        self._db = db
        if not kwargs:
            lifespan_coroutine = lifespan(self._db)
            self._app = FastAPI(lifespan=asynccontextmanager(lifespan_coroutine))
        else:
            self._app = FastAPI(**kwargs)

    @property
    def get_app(self) -> FastAPI:

        self._app.exception_handler(Exception)(unicorn_exception_handler)

        self._app.mount(
            "/css",
            StaticFiles(
                directory=os.path.join(self._dir_info["BASE_DIR_STATIC"], "css")
            ),
            name="css",
        )
        self._app.mount(
            "/js",
            StaticFiles(
                directory=os.path.join(self._dir_info["BASE_DIR_STATIC"], "js")
            ),
            name="js",
        )
        self._app.mount(
            "/images",
            StaticFiles(directory=self._dir_info["BASE_DIR_MEDIA"]),
            name="images",
        )

        GetDBDIRInfo.db = self._db
        GetDBDIRInfo.dir_info = self._dir_info

        self._app.include_router(
            router=static_html_router, dependencies=[Depends(GetDBDIRInfo)]
        )
        self._app.include_router(
            router=users_router, prefix="/api", dependencies=[Depends(GetDBDIRInfo)]
        )
        self._app.include_router(
            router=tweets_router, prefix="/api", dependencies=[Depends(GetDBDIRInfo)]
        )
        self._app.include_router(
            router=media_router, prefix="/api", dependencies=[Depends(GetDBDIRInfo)]
        )

        return self._app

    @property
    def get_db(self) -> DB:
        return self._db
