from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Like, Tweet, User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_dislike_tweet(client: AsyncClient, db: Database) -> None:
    """
    Проверяем route /api/tweets/<id>/likes метод delete. Убираем лайк твиту по его id.

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
        # Создадим твит.
        tweet_main = Tweet(
            author=main_user, content="".join(choices(ascii_letters, k=10))
        )
        # Лайкнем твит.
        main_like = Like(user=main_user)
        another_like = Like(user=another_user)
        tweet_main.likes.extend([main_like, another_like])
        session.add(tweet_main)
        await session.commit()
        assert tweet_main.id
        assert main_like.id
        assert another_like.id

        # Убираем лайк своему твиту.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.delete(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Проверим: удалился ли лайк.
        session.expunge(main_like)
        main_like_q = await session.execute(
            select(Like).where(
                Like.user_id == main_user.id, Like.tweet_id == tweet_main.id
            )
        )
        main_like_bd = main_like_q.scalars().one_or_none()
        assert main_like_bd is None

        # Убираем лайк чужому твиту.
        client.headers["api-key"] = another_user.api_key
        response = await client.delete(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Убираем лайк повторно.
        response = await client.delete(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 400
        data = response.json()
        assert data["result"] is False
