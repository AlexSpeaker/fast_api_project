import pytest
from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload

from manage_utils.create_user import create_user_one, create_users_auto
from my_twitter.app.database.database import DB
from my_twitter.app.database.models import User


@pytest.mark.asyncio
async def test_manage_func_create_user(db: DB):
    """Тестируем функции manage. create_user"""
    async with db.get_session() as session:
        user_data = dict(
            first_name="test_name",
            middle_name="test_middle_name",
            surname="test_surname",
            api_key="test_api_key",
        )
        await create_user_one(db, user_data)

        user_q = await session.execute(
            select(User)
            .where(
                and_(
                    User.first_name == user_data["first_name"],
                    User.surname == user_data["surname"],
                    User.middle_name == user_data["middle_name"],
                )
            )
            .options(joinedload(User.login))
        )

        user = user_q.scalars().one()

    assert user.first_name == user_data["first_name"]
    assert user.surname == user_data["surname"]
    assert user.middle_name == user_data["middle_name"]
    assert user.login.key == user_data["api_key"]


@pytest.mark.asyncio
async def test_manage_func_create_users_auto(db: DB):
    """Тестируем функции manage. create_users_auto"""
    async with db.get_session() as session:
        count = 10
        await create_users_auto(db, count)

        count_users_q = await session.execute(select(func.Count(User.id)))
        count_users = count_users_q.scalar()
    assert count_users == count + 10
