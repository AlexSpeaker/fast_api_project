from random import choice, choices, randint
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Attachment, User, Tweet, Like
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
        assert set(att.id for att in attachments) == set(att.id for att in tweet.attachments)

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
        tweets = [Tweet(author=main_user, content="".join(choices(ascii_letters, k=10))) for _ in range(50)]
        for tweet in tweets:
            tweet.attachments.append(Attachment(image_path="".join(choices(ascii_letters, k=10))))
            tweet.likes.append(Like(user=main_user))
        session.add_all(tweets)
        await session.commit()

    offset = 1
    limit = 5
    # Параметры запроса.
    params = {
        "offset": offset, # текущая страница.
        "limit": limit, # количество постов на страницу.
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
    assert data["tweets"][-1]["id"] == tweets_sorted[limit -1].id
    assert data["tweets"][0]["author"]["id"] == tweets_sorted[0].author.id
    assert tweets_sorted[0].author.surname in data["tweets"][0]["author"]["name"]
    assert data["tweets"][0]["likes"][0]["user_id"] == tweets_sorted[0].likes[0].user_id
    assert tweets_sorted[0].likes[0].user.first_name in data["tweets"][0]["likes"][0]["name"]

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
        tweet_main = Tweet(author=main_user, content="".join(choices(ascii_letters, k=10)))
        tweet_another = Tweet(author=another_user, content="".join(choices(ascii_letters, k=10)))
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
        tweet_main = tweet_main_q.scalars().one_or_none()
        assert tweet_main is None

        tweet_another_q = await session.execute(
            select(Tweet).where(Tweet.id == tweet_another.id)
        )
        tweet_another = tweet_another_q.scalars().one_or_none()
        assert tweet_another is not None

@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_like_tweet(client: AsyncClient, db: Database) -> None:
    """
    Проверяем route /api/tweets/<id>/likes метод post. Ставим лайк твиту по его id.

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
        tweet_main = Tweet(author=main_user, content="".join(choices(ascii_letters, k=10)))
        session.add(tweet_main)
        await session.commit()
        assert tweet_main.id

        # Ставим лайк своему твиту.
        client.headers.setdefault("api-key", main_user.api_key)
        response = await client.post(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Проверим есть ли лайк.
        main_like_q = await session.execute(
            select(Like).where(Like.user_id == main_user.id, Like.tweet_id == tweet_main.id)
        )
        main_like = main_like_q.scalars().one_or_none()
        assert main_like is not None

        # Ставим лайк чужому твиту.
        client.headers["api-key"] = another_user.api_key
        response = await client.post(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

        # Пробуем поставить лайк повторно.
        response = await client.post(f"/api/tweets/{tweet_main.id}/likes")
        assert response.status_code == 400
        data = response.json()
        assert data["result"] is False

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
        tweet_main = Tweet(author=main_user, content="".join(choices(ascii_letters, k=10)))
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
            select(Like).where(Like.user_id == main_user.id, Like.tweet_id == tweet_main.id)
        )
        main_like = main_like_q.scalars().one_or_none()
        assert main_like is None

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