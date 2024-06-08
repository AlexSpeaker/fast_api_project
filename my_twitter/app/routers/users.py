from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.params import Path
from sqlalchemy import select
from sqlalchemy.orm import subqueryload

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import User
from my_twitter.app.routers.schemas.user import UserOutSuccessfully, UserResultOutSchema
from my_twitter.app.utils.api_key import api_key_validator
from my_twitter.app.utils.dependencies import GetDBDIRInfo

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/users/me",
    response_model=UserOutSuccessfully,
    name="User data",
)
async def me_route(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)], request: Request
):
    """Роут для получения информации о себе."""
    db: DB = instance.get_db()

    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
    UserOutSuccessfully.user = user
    return UserOutSuccessfully


@router.get(
    "/users/{user_id}",
    response_model=UserOutSuccessfully,
    name="User data",
)
async def get_user(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    user_id: Annotated[int, Path(..., gt=0)],
):
    """Роут для получения информации о пользователе."""
    db: DB = instance.get_db()

    async with db.get_session() as session:
        user_q = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                subqueryload(User.my_subscriptions),
                subqueryload(User.my_subscribers),
            )
        )
        user: User = user_q.scalars().one()
    UserOutSuccessfully.user = user
    return UserOutSuccessfully


@router.post(
    "/users/{user_id}/follow",
    response_model=UserResultOutSchema,
    name="Follow another user",
)
async def follow_another_user(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    user_id: Annotated[int, Path(..., gt=0)],
    request: Request,
):
    """Роут для подписки на другого пользователя."""
    db: DB = instance.get_db()
    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)

        user_follow_q = await session.execute(select(User).where(User.id == user_id))
        user_follow: User = user_follow_q.scalars().one()
        user.users_in_my_subscriptions.append(user_follow)
        await session.commit()
    UserResultOutSchema.result = True
    return UserResultOutSchema


@router.delete(
    "/users/{user_id}/follow",
    response_model=UserResultOutSchema,
    name="Unsubscribe from another user",
)
async def unsubscribe_from_another_user(
    instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)],
    user_id: Annotated[int, Path(..., gt=0)],
    request: Request,
):
    """Роут для отписки от другого пользователя."""
    db: DB = instance.get_db()
    async with db.get_session() as session:
        user = await api_key_validator(request.headers.get("api-key"), session)
        user_follow_q = await session.execute(select(User).where(User.id == user_id))
        user_follow: User = user_follow_q.scalars().one()
        user.users_in_my_subscriptions.remove(user_follow)
        await session.commit()
    UserResultOutSchema.result = True
    return UserResultOutSchema
