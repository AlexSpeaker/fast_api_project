import pytest
from app.database.database import Database
from app.database.models import User
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.models
@pytest.mark.asyncio
async def test_add_subscription(db: Database) -> None:
    """
    Попробуем на кого-нибудь подписаться.
    Мы точно знаем, что у нас есть 10 пользователей.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Достаём всех пользователей.
        users_q = await session.execute(
            select(User).options(subqueryload(User.my_subscriptions))
        )
        users = users_q.scalars().all()
        assert len(users) == 10
        # Определяем пользователя для теста.
        main_user = users[0]
        # Убедимся, что пользователь ни на кого не подписан.
        assert not main_user.users_in_my_subscriptions
        # Определяем пользователя для подписки.
        subscription_user = users[1]
        # Подписываемся.
        main_user.users_in_my_subscriptions.append(subscription_user)
        await session.commit()

        # Ради чистоты теста достаём нашего пользователя ещё раз.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(subqueryload(User.my_subscriptions))
        )
        user = user_q.scalars().one()
        # Убедимся он ли это.
        assert user.id == main_user.id
        # Убедимся, что в подписках ожидаемый пользователь.
        assert len(user.users_in_my_subscriptions) == 1
        assert user.users_in_my_subscriptions[0].id == subscription_user.id
