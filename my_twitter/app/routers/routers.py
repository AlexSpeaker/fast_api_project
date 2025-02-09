from typing import Tuple

from app.routers.users import router as user_router
from fastapi import APIRouter

routers: Tuple[APIRouter] = (user_router,)
