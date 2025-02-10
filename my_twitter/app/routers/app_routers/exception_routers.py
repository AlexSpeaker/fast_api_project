from fastapi import APIRouter

debug_router = APIRouter(
    tags=["exceptions"],
)


@debug_router.get(
    "/try_me",
    description="Роут-исключение для проверки хендлера исключений. ZeroDivisionError.",
    responses={
        500: {"description": "Internal Server Error"},
    },
    response_model=None,
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
    responses={
        500: {"description": "Internal Server Error"},
    },
    response_model=None,
)
async def try_me_route_2() -> None:
    """
    Роут-исключение для проверки хендлера исключений. ValueError.
    :return: None.
    """
    raise ValueError("Не верный параметр.")
