from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Like, Tweet, User
from app.database.models.tweet import MAX_TWEET_LENGTH
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.models
@pytest.mark.asyncio
async def test_add_like(db: Database) -> None:
    """
    Попробуем поставить лайк твиту.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Получаем пользователя.
        users_q = await session.execute(select(User).limit(1).order_by(User.id))
        users = users_q.scalars().all()
        assert len(users) == 1
        main_user = users[0]
        # Создаём твит.
        tweet = Tweet(
            content="".join(choices(ascii_letters, k=MAX_TWEET_LENGTH - 1)),
            author=main_user,
        )
        session.add(tweet)
        await session.commit()
        # Лайкаем твит.
        like = Like(user=main_user, tweet=tweet)
        session.add(like)
        await session.commit()

        # Ради чистоты теста достаём наш твит из БД.
        session.expunge(tweet)
        tweet_q = await session.execute(
            select(Tweet).where(Tweet.id == tweet.id).options(subqueryload(Tweet.likes))
        )
        tweet_bd = tweet_q.scalars().one()
        # Убедимся он ли это.
        assert tweet_bd.id == tweet.id
        # Смотрим лайк.
        assert len(tweet_bd.likes) == 1
        assert tweet_bd.likes[0].user == main_user
