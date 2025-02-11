from app.application.classes import CustomFastApi
from app.routers.app_routers.schemas.users import OutUserSchema, UserSchema
from app.utils.utils import get_user_or_test_user
from fastapi import APIRouter, Request

router = APIRouter(tags=["users"])


@router.get(
    "/users/me",
    response_model=OutUserSchema,
    name="User data",
)
async def me_route(request: Request) -> OutUserSchema:
    """
    Функция вернёт информацию о пользователе.
    Api-key передаётся в headers.
    Если по какой-то причине api-key не передан или в БД не нашёлся соответствующий пользователь,
    то функция вернёт информацию об тестовом пользователе, который всегда есть.
    Это сделано из-за особенности 'фронта', он ломается, если пользователя нет вообще.

    :param request: Request.
    :return: OutUserSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    api_key = request.headers.get("api-key") or "test"
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, app.get_settings(), api_key)
    return OutUserSchema(user=UserSchema.model_validate(user))
