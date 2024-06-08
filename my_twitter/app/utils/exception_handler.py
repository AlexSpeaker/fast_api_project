from fastapi import Request
from starlette.responses import JSONResponse


async def unicorn_exception_handler(request: Request, exc):
    return JSONResponse(
        {
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
