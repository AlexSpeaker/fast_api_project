import pytest
from app.database.database import Database
from app.database.models import User
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.models
@pytest.mark.asyncio
async def test_subscriber(db: Database) -> None:
    """
    Проверяем подписчиков.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Достаём всех пользователей.
        users_q = await session.execute(
            select(User).options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        assert len(users) == 10
        # Определяем пользователя для теста.
        main_user = users[0]
        # Убедимся, что на него никто не подписан.
        assert not main_user.users_following_me
        # Подпишемся на него.
        subscriber_1 = users[1]
        subscriber_2 = users[2]
        subscriber_1.users_in_my_subscriptions.append(main_user)
        subscriber_2.users_in_my_subscriptions.append(main_user)
        await session.commit()

        # Ради чистоты теста достаём нашего пользователя ещё раз.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
        # Убедимся он ли это.
        assert user.id == main_user.id
        # Убедимся, что на него подписаны 2 пользователя.
        assert len(user.users_following_me) == 2
        assert {subscriber_1.id, subscriber_2.id} == set(
            subscriber.id for subscriber in user.users_following_me
        )
