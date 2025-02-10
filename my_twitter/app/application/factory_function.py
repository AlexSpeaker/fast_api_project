from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Sequence

from app.application.classes import CustomFastApi
from app.application.lifespan import lifespan_func
from app.database.database import Database
from app.database.database import db as database
from app.routers.exception_handlers import (
    generic_exception_handler,
    http_exception_handler,
)
from app.routers.routers import routers
from app.settings.classes import Settings
from app.settings.settings import settings as app_settings
from fastapi import APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles


def get_app(
    *args: Any,
    settings: Settings = app_settings,
    db: Database = database,
    lifespan: Callable[
        [CustomFastApi], AbstractAsyncContextManager[None]
    ] = lifespan_func,
    routers_sequence: Sequence[APIRouter] = routers,
    **kwargs: Any,
) -> CustomFastApi:
    app = CustomFastApi(*args, db=db, settings=settings, lifespan=lifespan, **kwargs)
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(Exception)(generic_exception_handler)
    if settings.DEBUG:
        app.mount(
            settings.STATIC_URL,
            StaticFiles(directory=settings.STATIC_ROOT, html=True),
            name="static",
        )
        app.mount(
            f"{settings.MEDIA_URL}images",
            StaticFiles(directory=settings.MEDIA_ROOT / settings.IMAGES_FOLDER_NAME),
            name="images",
        )
    for router in routers_sequence:
        app.include_router(router=router, prefix="/api")
    return app
