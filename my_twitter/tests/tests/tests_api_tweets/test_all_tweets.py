from random import choice, choices, randint
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Attachment, Like, Tweet, User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_all_tweets(client: AsyncClient, db: Database) -> None:
    """
    Проверяем роут /api/tweets метод get.
    Ожидаем все твиты отсортированные по дате в порядке убывания.

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
        # Создадим 50 твитов (для проверки пагинации.)
        tweets = [
            Tweet(author=main_user, content="".join(choices(ascii_letters, k=10)))
            for _ in range(50)
        ]
        for tweet in tweets:
            tweet.attachments.append(
                Attachment(image_path="".join(choices(ascii_letters, k=10)))
            )
            tweet.likes.append(Like(user=main_user))
        session.add_all(tweets)
        await session.commit()

    offset = 1
    limit = 5
    # Параметры запроса.
    params = {
        "offset": offset,  # текущая страница.
        "limit": limit,  # количество постов на страницу.
    }
    # Делаем запрос.
    response = await client.get("/api/tweets", params=params)
    assert response.status_code == 200

    # Проверяем всё ли на месте.
    tweets_sorted = sorted(tweets, key=lambda t: t.created, reverse=True)
    data = response.json()
    assert set(data.keys()) == {"result", "tweets"}
    assert data["result"] is True
    assert set(data["tweets"][0].keys()) == {
        "id",
        "content",
        "attachments",
        "author",
        "likes",
    }
    assert len(data["tweets"]) == limit
    assert len(data["tweets"][0]["attachments"]) == 1
    assert len(data["tweets"][0]["likes"]) == 1
    assert data["tweets"][0]["id"] == tweets_sorted[0].id
    assert data["tweets"][-1]["id"] == tweets_sorted[limit - 1].id
    assert data["tweets"][0]["author"]["id"] == tweets_sorted[0].author.id
    assert tweets_sorted[0].author.surname in data["tweets"][0]["author"]["name"]
    assert data["tweets"][0]["likes"][0]["user_id"] == tweets_sorted[0].likes[0].user_id
    assert (
        tweets_sorted[0].likes[0].user.first_name
        in data["tweets"][0]["likes"][0]["name"]
    )

    # Откроем 5 раз рандомно.
    for _ in range(5):
        offset = randint(1, 5)
        limit = randint(1, 10)
        # Параметры запроса.
        params = {
            "offset": offset,  # текущая страница.
            "limit": limit,  # количество постов на страницу.
        }
        # Делаем запрос.
        response = await client.get("/api/tweets", params=params)
        assert response.status_code == 200
        data = response.json()

        assert len(data["tweets"]) == limit
        assert data["tweets"][0]["id"] == tweets_sorted[(offset - 1) * limit].id
        assert data["tweets"][-1]["id"] == tweets_sorted[offset * limit - 1].id
