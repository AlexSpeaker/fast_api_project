import pytest
from app.database.database import Database
from app.database.models import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_delete_a_subscription(client: AsyncClient, db: Database) -> None:
    """
    Тестируем роут api/users/<id>/follow метод delete.
    Ожидание: текущий пользователь отпишется от пользователя по id.

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
        main_user = users[3]
        another_user = users[1]
        # Сделаем подписку.
        main_user.users_in_my_subscriptions.append(another_user)
        await session.commit()

        # Делаем запрос.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.delete(f"api/users/{another_user.id}/follow")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Проверяем, что main_user действительно отписался от another_user.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
        assert not user.users_in_my_subscriptions

        # Попробуем выполнить запрос ещё раз.
        # Ожидаем ошибку.
        response = await client.delete(f"api/users/{another_user.id}/follow")
        assert response.status_code == 400
