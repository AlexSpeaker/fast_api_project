import pytest
from app.database.database import Database
from app.database.models import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_information_about_the_user_by_id(
    client: AsyncClient, db: Database
) -> None:
    """
    Тестируем роут api/users/<id> метод get.
    Ожидаем информацию о пользователе по его id.

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
        assert users
        # Определим пользователя для теста.
        main_user = users[3]
        # Подпишем его на 2-х пользователей.
        main_user.users_in_my_subscriptions.extend(users[4:6])
        # И сделаем, что на нашего пользователя подписаны 3 пользователя.
        for i in range(6, 9):
            users[i].users_in_my_subscriptions.append(main_user)
        await session.commit()
    # Делаем запрос о пользователе по id.
    response = await client.get(f"/api/users/{main_user.id}")
    assert response.status_code == 200
    data = response.json()
    # Проверяем, всё ли на месте.
    assert data["result"] is True
    assert data["user"]["id"] == main_user.id
    assert main_user.first_name in data["user"]["name"]
    assert main_user.middle_name in data["user"]["name"]
    assert main_user.surname in data["user"]["name"]

    assert len(data["user"]["following"]) == 2
    assert len(data["user"]["followers"]) == 3
    assert data["user"]["following"][0]["id"]
    assert data["user"]["following"][0]["name"]
