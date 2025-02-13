import pytest
from app.database.database import Database
from app.database.models import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_information_about_the_current_user(
    client: AsyncClient, db: Database
) -> None:
    """
    Тестируем роут api/users/me метод get.
    Ожидаем информацию о пользователе.

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
        main_user = users[0]
        # Подпишем его на 2-х пользователей.
        main_user.users_in_my_subscriptions.extend(users[1:3])
        # И сделаем, что на нашего пользователя подписаны 3 пользователя.
        for i in range(3, 6):
            users[i].users_in_my_subscriptions.append(main_user)
        await session.commit()
    # Делаем запрос о нашем пользователе.
    client.headers.setdefault("api-key", main_user.api_key)
    response = await client.get("/api/users/me")
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
