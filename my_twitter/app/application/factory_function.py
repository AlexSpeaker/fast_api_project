from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Sequence

from app.application.classes import CustomFastApi
from app.application.lifespan import lifespan_func
from app.database.database import Database
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
    lifespan: Callable[
        [CustomFastApi], AbstractAsyncContextManager[None]
    ] = lifespan_func,
    routers_sequence: Sequence[APIRouter] = routers,
    **kwargs: Any,
) -> CustomFastApi:
    db = Database(db_url=settings.DB_SETTINGS.DATABASE_URL)
    app = CustomFastApi(*args, db=db, settings=settings, lifespan=lifespan, **kwargs)
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(Exception)(generic_exception_handler)
    if settings.DEBUG:
        app.mount(
            "/",
            StaticFiles(directory=settings.STATIC_ROOT, html=True),
            name="static",
        )
        app.mount(
            "/images",
            StaticFiles(directory=settings.MEDIA_ROOT / "images"),
            name="images",
        )
    for router in routers_sequence:
        app.include_router(router=router, prefix="/api")
    return app
