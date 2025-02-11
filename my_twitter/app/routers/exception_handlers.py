from app.application.classes import CustomFastApi
from fastapi import Request
from starlette.responses import JSONResponse


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Хендлер исключений. Сработает, если в приложении возникнет ошибка Exception.

    :param request: Request.
    :param exc: Exception.
    :return: JSONResponse.
    """
    app: CustomFastApi = request.app
    loger = app.get_logger("exception_handler")
    loger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "result": False,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc) if app.get_settings().DEBUG else "Error",
        },
    )
