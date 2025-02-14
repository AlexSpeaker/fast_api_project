from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Tweet, User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_delete_tweet(client: AsyncClient, db: Database) -> None:
    """
    Проверяем роут /api/tweets/<id> метод delete.
    Ожидаем, что автор может удалить свой твит по id.

    :param client: AsyncClient.
    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Получим всех пользователей.
        users_q = await session.execute(
            select(User).options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        # Определим пользователей для теста.
        main_user = users[0]
        another_user = users[1]
        # Создадим твиты пользователей.
        tweet_main = Tweet(
            author=main_user, content="".join(choices(ascii_letters, k=10))
        )
        tweet_another = Tweet(
            author=another_user, content="".join(choices(ascii_letters, k=10))
        )
        session.add_all([tweet_main, tweet_another])
        await session.commit()
        assert tweet_main.id
        assert tweet_another.id

        # Делаем запрос.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.delete(f"/api/tweets/{tweet_main.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Пробуем удалить твит другого пользователя.
        response = await client.delete(f"/api/tweets/{tweet_another.id}")
        assert response.status_code == 400
        data = response.json()
        assert data["result"] is False

        # Проверим, что действительно tweet_main удалён, а tweet_another есть в БД.
        session.expunge(tweet_main)
        session.expunge(tweet_another)

        tweet_main_q = await session.execute(
            select(Tweet).where(Tweet.id == tweet_main.id)
        )
        tweet_main_bd = tweet_main_q.scalars().one_or_none()
        assert tweet_main_bd is None

        tweet_another_q = await session.execute(
            select(Tweet).where(Tweet.id == tweet_another.id)
        )
        tweet_another_bd = tweet_another_q.scalars().one_or_none()
        assert tweet_another_bd is not None
