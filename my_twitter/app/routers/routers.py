from typing import Sequence

from app.routers.app_routers.exception_routers import debug_router
from app.routers.app_routers.users import router as user_router
from fastapi import APIRouter

routers: Sequence[APIRouter] = (user_router, debug_router)
