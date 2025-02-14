from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Tweet, User
from app.database.models.tweet import MAX_TWEET_LENGTH
from sqlalchemy import select
from sqlalchemy.orm import subqueryload


@pytest.mark.models
@pytest.mark.asyncio
async def test_add_tweet(db: Database) -> None:
    """
    Попробуем создать tweet.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:

        # Получаем пользователя.
        users_q = await session.execute(select(User).limit(1).order_by(User.id))
        users = users_q.scalars().all()
        assert len(users) == 1
        main_user = users[0]

        # Тут при попытке создать твит с текстом больше установленного размера ожидаем исключение.
        with pytest.raises(ValueError):
            Tweet(
                content="".join(choices(ascii_letters, k=MAX_TWEET_LENGTH + 1)),
                author=main_user,
            )

        # создаём твит.
        tweet = Tweet(
            content="".join(choices(ascii_letters, k=MAX_TWEET_LENGTH - 1)),
            author=main_user,
        )
        session.add(tweet)
        await session.commit()

        # Ради чистоты теста достаём нашего пользователя ещё раз.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(subqueryload(User.tweets))
        )
        user = user_q.scalars().one()
        # Убедимся он ли это.
        assert user.id == main_user.id
        # Убедимся наш ли твит.
        assert len(user.tweets) == 1
        assert user.tweets[0].content == tweet.content
        assert user.tweets[0].id == tweet.id
