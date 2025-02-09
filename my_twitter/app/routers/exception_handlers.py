from app.application.classes import CustomFastApi
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    app: CustomFastApi = request.app
    return JSONResponse(
        status_code=exc.status_code,
        content=({"message": exc.detail if app.get_settings().DEBUG else "Error"}),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app: CustomFastApi = request.app
    return JSONResponse(
        status_code=500,
        content=({"message": str(exc) if app.get_settings().DEBUG else "Error"}),
    )
