from fastapi import APIRouter, HTTPException

debug_router = APIRouter(
    tags=["exceptions"],
)


@debug_router.get(
    "/try_me",
    description="Роут-исключение для проверки хендлера исключений. ZeroDivisionError.",
)
async def try_me_route() -> None:
    """
    Роут-исключение для проверки хендлера исключений. ZeroDivisionError.
    :return: None.
    """
    raise ZeroDivisionError("Деление на ноль.")


@debug_router.get(
    "/try_me_2",
    description="Роут-исключение для проверки хендлера исключений. ValueError.",
)
async def try_me_route_2() -> None:
    """
    Роут-исключение для проверки хендлера исключений. ValueError.
    :return: None.
    """
    raise ValueError("Не верный параметр.")


@debug_router.get(
    "/try_me_3",
    description="Роут-исключение для проверки хендлера исключений. HTTPException.",
)
async def try_me_route_3() -> None:
    """
    Роут-исключение для проверки хендлера исключений. HTTPException.
    :return: None.
    """
    raise HTTPException(status_code=404, detail="Не верный запрос.")
