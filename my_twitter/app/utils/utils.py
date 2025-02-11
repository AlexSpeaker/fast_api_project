from typing import Any, Dict, Type

from app.database.models import User
from app.settings.classes import Settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload


class ImageManager:
    def __init__(
        self,
        settings: Settings,
    ):
        pass


async def get_or_create[T](
    session: AsyncSession, model: Type[T], data: Dict[str, Any]
) -> tuple[bool, T]:
    """
    Функция вернёт объект модели по заданным параметрам, если такой существует, в противном случае создаст его.

    :param session: AsyncSession.
    :param model: Модель базы данных.
    :param data: Данные модели.
    :return: (True, object) - если объект был создан, иначе (False, object)
    """
    obj_q = await session.execute(select(model).filter_by(**data))
    obj = obj_q.scalars().first()
    if obj:
        return False, obj
    new_obj = model(**data)
    session.add(new_obj)
    await session.commit()
    return True, new_obj


async def get_or_create_test_user(
    session: AsyncSession, settings: Settings
) -> tuple[bool, User]:
    """
    Функция возвращает тестового пользователя. Если он ещё не существует, то создаст его.

    :param session: AsyncSession.
    :param settings: Settings.
    :return: (True, User) - если объект был создан, иначе (False, User)
    """
    test_user = settings.TEST_USER
    return await get_or_create(
        session,
        User,
        dict(
            api_key=test_user.api_key,
            first_name=test_user.first_name,
            surname=test_user.surname,
            middle_name=test_user.middle_name,
        ),
    )


async def get_user_or_test_user(
    session: AsyncSession, settings: Settings, api_key: str
) -> User:
    """
    Вернёт пользователя с заданным api_key.
    Если такого пользователя нет, то вернёт тестового пользователя.

    :param session: AsyncSession.
    :param settings: Settings.
    :param api_key: Api_key пользователя.
    :return: User.
    """
    user_q = await session.execute(
        select(User)
        .where(User.api_key == api_key)
        .options(subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions))
    )
    user = user_q.scalars().one_or_none()
    if not user:
        user_q = await session.execute(
            select(User)
            .where(User.api_key == settings.TEST_USER.api_key)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
    return user
