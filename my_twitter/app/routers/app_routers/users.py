from typing import Annotated

from app.database.database import Database
from app.database.models import User
from app.routers.app_routers.schemas.base import BaseSchema
from app.routers.app_routers.schemas.users import OutUserSchema, UserSchema
from app.settings.classes import Settings
from app.utils.utils import (
    get_database,
    get_settings,
    get_user_or_test_user,
    get_user_with_apikey_and_user_with_id,
)
from fastapi import APIRouter, Header, HTTPException, Path
from fastapi.params import Depends
from sqlalchemy import select
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
async def me_route(
    db: Annotated[Database, Depends(get_database)],
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str, Header(...)] = "test",
) -> OutUserSchema:
    """
    Функция вернёт информацию о пользователе.

    Если в БД не нашёлся соответствующий пользователь,
    то функция вернёт информацию об тестовом пользователе, который всегда есть.
    Это сделано из-за особенности 'фронта', он ломается, если пользователя нет вообще.

    :param db: Инструмент работы с БД.
    :param settings: Настройки приложения.
    :param api_key: API key пользователя.
    :return: OutUserSchema.
    """
    async with db.get_sessionmaker() as session:
        user = await get_user_or_test_user(session, settings, api_key)
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
    db: Annotated[Database, Depends(get_database)],
    user_id: Annotated[int, Path(..., gt=0)],
) -> OutUserSchema:
    """
    Функция вернёт информацию о пользователе по id.

    :param db: Инструмент работы с БД.
    :param user_id: ID пользователя.
    :return: OutUserSchema.
    """
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
    db: Annotated[Database, Depends(get_database)],
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str, Header(...)] = "test",
) -> BaseSchema:
    """
    Функция оформит подписку текущего пользователя на пользователя с переданным id.

    :param user_id: ID пользователя.
    :param db: Инструмент работы с БД.
    :param settings: Настройки приложения.
    :param api_key: API key пользователя.
    :return: BaseSchema.
    """
    async with db.get_sessionmaker() as session:
        user_api, another_user = await get_user_with_apikey_and_user_with_id(
            session=session,
            api_key=api_key,
            user_id=user_id,
            settings=settings,
        )
        if (
            user_api.id == another_user.id
            or another_user in user_api.users_in_my_subscriptions
        ):
            raise HTTPException(status_code=400, detail="Не верный запрос.")
        user_api.users_in_my_subscriptions.append(another_user)
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
    db: Annotated[Database, Depends(get_database)],
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str, Header(...)] = "test",
) -> BaseSchema:
    """
    Функция отпишет текущего пользователя от пользователя с переданным id.

    :param user_id: ID пользователя.
    :param db: Инструмент работы с БД.
    :param settings: Настройки приложения.
    :param api_key: API key пользователя.
    :return: BaseSchema.
    """
    async with db.get_sessionmaker() as session:
        user_api, another_user = await get_user_with_apikey_and_user_with_id(
            session=session,
            api_key=api_key,
            user_id=user_id,
            settings=settings,
        )
        if (
            user_api.id == another_user.id
            or another_user not in user_api.users_in_my_subscriptions
        ):
            raise HTTPException(status_code=400, detail="Не верный запрос.")
        user_api.users_in_my_subscriptions.remove(another_user)
        await session.commit()

    return BaseSchema()
