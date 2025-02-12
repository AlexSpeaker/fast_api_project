from typing import Annotated

from app.application.classes import CustomFastApi
from app.database.models import User
from app.routers.app_routers.schemas.base import BaseSchema
from app.routers.app_routers.schemas.users import OutUserSchema, UserSchema
from app.utils.utils import get_user_or_test_user
from fastapi import APIRouter, Path, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import subqueryload

router = APIRouter(tags=["users"])


@router.get(
    "/users/me",
    response_model=OutUserSchema,
    description="Предоставляет информацию о текущем пользователе (по умолчанию тестовый пользователь), "
    "а также информацию о пользователях на которых подписан пользователь и пользователях, "
    "которые подписаны на текущего пользователя.",
    name="Информация о текущем пользователе",
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


@router.get(
    "/users/{user_id}",
    response_model=OutUserSchema,
    description="Предоставляет информацию о пользователе по id, "
    "а также информацию о пользователях на которых подписан этот пользователь и пользователях, "
    "которые подписаны на этого пользователя.",
    name="Информация о пользователе по id.",
)
async def get_user(
    request: Request,
    user_id: Annotated[int, Path(..., gt=0)],
) -> OutUserSchema:
    """
    Функция вернёт информацию о пользователе по id.

    :param request: Request.
    :param user_id: ID пользователя.
    :return: OutUserSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    async with db.get_sessionmaker() as session:
        user_q = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
    return OutUserSchema(user=UserSchema.model_validate(user))


@router.post(
    "/users/{user_id}/follow",
    response_model=BaseSchema,
    description="Подпишет текущего пользователя (по умолчанию тестовый пользователь) на пользователя с переданным id.",
    name="Подписка на другого пользователя.",
)
async def follow_another_user(
    user_id: Annotated[int, Path(..., gt=0)],
    request: Request,
) -> BaseSchema:
    """
    Функция оформит подписку текущего пользователя на пользователя с переданным id.

    :param user_id: ID пользователя.
    :param request: Request.
    :return: BaseSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    api_key = request.headers.get("api-key") or "test"
    async with db.get_sessionmaker() as session:
        users_q = await session.execute(
            select(User)
            .where(or_((User.id == user_id), (User.api_key == api_key)))
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        if len(users) != 2:
            return BaseSchema(result=False)
        elif users[0].id == user_id:
            users[1].users_in_my_subscriptions.append(users[0])
        else:
            users[0].users_in_my_subscriptions.append(users[1])
        await session.commit()

    return BaseSchema()


@router.delete(
    "/users/{user_id}/follow",
    response_model=BaseSchema,
    description="Отпишет текущего пользователя (по умолчанию тестовый пользователь) от пользователя с переданным id.",
    name="Отписка от другого пользователя.",
)
async def unsubscribe_from_another_user(
    user_id: Annotated[int, Path(..., gt=0)],
    request: Request,
) -> BaseSchema:
    """
    Функция отпишет текущего пользователя от пользователя с переданным id.

    :param user_id: ID пользователя.
    :param request: Request.
    :return: BaseSchema.
    """
    app: CustomFastApi = request.app
    db = app.get_db()
    api_key = request.headers.get("api-key") or "test"
    async with db.get_sessionmaker() as session:
        users_q = await session.execute(
            select(User)
            .where(or_((User.id == user_id), (User.api_key == api_key)))
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        if len(users) != 2:
            return BaseSchema(result=False)
        elif users[0].id == user_id:
            users[1].users_in_my_subscriptions.remove(users[0])
        else:
            users[0].users_in_my_subscriptions.remove(users[1])
        await session.commit()

    return BaseSchema()
