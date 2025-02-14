from random import choice

import pytest
from app.database.database import Database
from app.database.models import Attachment, Tweet, User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_tweet_create(client: AsyncClient, db: Database) -> None:
    """
    Проверяем роут /api/tweets метод post.
    Ожидаем создание твита.

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
        # Определим пользователя для теста.
        main_user = choice(users)
        # Создадим вложения (они создаются до сохранения твита, нам нужны только их id)
        attachments = [Attachment(image_path="Тут яко-бы путь...") for _ in range(3)]
        session.add_all(attachments)
        await session.commit()

        # Подготовим тело запроса.
        request_data = {
            "tweet_data": "Text",
            "tweet_media_ids": [att.id for att in attachments],
        }
        # Делаем запрос.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.post("/api/tweets", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Проверим, что твит действительно создан.
        tweet_q = await session.execute(
            select(Tweet).where(Tweet.id == data["tweet_id"])
        )
        tweet = tweet_q.scalars().one_or_none()
        assert tweet is not None
        assert set(att.id for att in attachments) == set(
            att.id for att in tweet.attachments
        )
