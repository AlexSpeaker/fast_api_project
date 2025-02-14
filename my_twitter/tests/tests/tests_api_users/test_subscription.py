import pytest
from app.database.database import Database
from app.database.models import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_subscription(client: AsyncClient, db: Database) -> None:
    """
    Тестируем роут api/users/<id>/follow метод post.
    Ожидание: текущий пользователь подпишется на пользователя по id.

    :param client: AsyncClient.
    :param db: Database.
    :return: None.
    """
    # Получим всех пользователей.
    async with db.get_sessionmaker() as session:
        users_q = await session.execute(
            select(User).options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        # Определим пользователей для теста.
        main_user = users[0]
        another_user = users[5]
        # Делаем запрос.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.post(f"api/users/{another_user.id}/follow")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        # Проверяем, что main_user действительно подписался на another_user.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
        assert user.users_in_my_subscriptions[0].id == another_user.id

        # Попробуем выполнить запрос ещё раз.
        # Ожидаем ошибку.
        response = await client.post(f"api/users/{another_user.id}/follow")
        assert response.status_code == 400
