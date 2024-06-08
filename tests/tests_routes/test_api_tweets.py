import pytest
from sqlalchemy import func

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import Attachment, Like, Tweet


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_create(client, db: DB, other_users):
    """Проверяем route /api/tweets. Создаём tweet."""
    client.headers.setdefault("api-key", other_users[0])
    async with db.get_session() as session:
        attachments = [
            Attachment(image_url=f"/{other_users[0]}/{i}.png") for i in range(3)
        ]
        session.add_all(attachments)
        await session.commit()
        data = {
            "tweet_data": "Text",
            "tweet_media_ids": [attachment.id for attachment in attachments],
        }
        response = await client.post("/api/tweets", json=data)
        assert response.json()["result"]
        assert response.json()["tweet_id"]
        count_q = await session.execute(func.Count(Tweet.id))
        count = count_q.scalar()
        assert count == 2


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_get_tweets(client, other_users):
    """Проверяем route /api/tweets. Получаем все tweets."""
    client.headers.setdefault("api-key", other_users[0])
    response = await client.get("/api/tweets")
    assert set(response.json().keys()) == {"result", "tweets"}
    assert response.json()["result"]
    assert set(response.json()["tweets"][0].keys()) == {
        "id",
        "content",
        "attachments",
        "author",
        "likes",
    }


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_delete_tweet_your_tweet(client, other_users, db: DB):
    """Проверяем route /api/tweets. Удалим свой твит"""
    client.headers.setdefault("api-key", other_users[0])
    response = await client.delete("/api/tweets/1")
    assert response.status_code == 200
    assert response.json()["result"]
    async with db.get_session() as session:
        count_q = await session.execute(func.Count(Tweet.id))
        count = count_q.scalar()
        assert count == 0


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_delete_tweet_no_your_tweet(client, other_users):
    """Проверяем route /api/tweets. Удалим чужой твит"""
    client.headers.setdefault("api-key", other_users[1])
    response = await client.delete("/api/tweets/1")
    assert response.status_code != 200


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_like(client, other_users, db: DB):
    """Проверяем route /api/tweets/<id>/likes. Ставим лайк."""
    client.headers.setdefault("api-key", other_users[0])
    response = await client.post("/api/tweets/1/likes")
    assert response.status_code == 200
    assert response.json()["result"]
    async with db.get_session() as session:
        count_q = await session.execute(func.Count(Like.id))
        count = count_q.scalar()
    assert count == 2


@pytest.mark.api_tweets
@pytest.mark.asyncio
async def test_route_api_tweets_dislike(client, other_users, db: DB):
    """Проверяем route /api/tweets/<id>/likes. Убираем лайк."""
    client.headers.setdefault("api-key", other_users[1])
    response = await client.delete("/api/tweets/1/likes")
    assert response.status_code == 200
    assert response.json()["result"]
    async with db.get_session() as session:
        count_q = await session.execute(func.Count(Like.id))
        count = count_q.scalar()
    assert count == 0
