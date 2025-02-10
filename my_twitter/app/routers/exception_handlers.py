from app.application.classes import CustomFastApi
from fastapi import Request
from starlette.responses import JSONResponse


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app: CustomFastApi = request.app
    return JSONResponse(
        status_code=500,
        content={"error_message": str(exc) if app.get_settings().DEBUG else "Error"},
    )
