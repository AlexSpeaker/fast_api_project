from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.application.classes import CustomFastApi


@asynccontextmanager
async def lifespan_func(app: CustomFastApi) -> AsyncGenerator[None, None]:
    print("Starting up...")
    yield
    print("Shutting down...")
