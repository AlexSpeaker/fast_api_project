from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Attachment, Like, Tweet, User
from app.database.models.tweet import MAX_TWEET_LENGTH
from sqlalchemy import select
from sqlalchemy.orm import subqueryload
from tests.utils import create_attachment_tweet_like


@pytest.mark.models
@pytest.mark.asyncio
async def test_create_user(db: Database) -> None:
    """
    Проверяем модель. Создаём юзера.

    :param db: Database.
    :return: None.
    """
    user: User = User(
        first_name="Александр",
        middle_name="Анатольевич",
        surname="Петров",
        api_key="test_user",
    )
    async with db.get_sessionmaker() as session:
        session.add(user)
        await session.commit()
    assert user.id


@pytest.mark.models
@pytest.mark.asyncio
async def test_add_subscription(db: Database) -> None:
    """
    Попробуем на кого-нибудь подписаться.
    Мы точно знаем, что у нас есть 10 пользователей.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Достаём всех пользователей.
        users_q = await session.execute(
            select(User).options(subqueryload(User.my_subscriptions))
        )
        users = users_q.scalars().all()
        assert len(users) == 10
        # Определяем пользователя для теста.
        main_user = users[0]
        # Убедимся, что пользователь ни на кого не подписан.
        assert not main_user.users_in_my_subscriptions
        # Определяем пользователя для подписки.
        subscription_user = users[1]
        # Подписываемся.
        main_user.users_in_my_subscriptions.append(subscription_user)
        await session.commit()

        # Ради чистоты теста достаём нашего пользователя ещё раз.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(subqueryload(User.my_subscriptions))
        )
        user = user_q.scalars().one()
        # Убедимся он ли это.
        assert user.id == main_user.id
        # Убедимся, что в подписках ожидаемый пользователь.
        assert len(user.users_in_my_subscriptions) == 1
        assert user.users_in_my_subscriptions[0].id == subscription_user.id


@pytest.mark.models
@pytest.mark.asyncio
async def test_subscriber(db: Database) -> None:
    """
    Проверяем подписчиков.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        # Достаём всех пользователей.
        users_q = await session.execute(
            select(User).options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        users = users_q.scalars().all()
        assert len(users) == 10
        # Определяем пользователя для теста.
        main_user = users[0]
        # Убедимся, что на него никто не подписан.
        assert not main_user.users_following_me
        # Подпишемся на него.
        subscriber_1 = users[1]
        subscriber_2 = users[2]
        subscriber_1.users_in_my_subscriptions.append(main_user)
        subscriber_2.users_in_my_subscriptions.append(main_user)
        await session.commit()

        # Ради чистоты теста достаём нашего пользователя ещё раз.
        session.expunge(main_user)
        user_q = await session.execute(
            select(User)
            .where(User.id == main_user.id)
            .options(
                subqueryload(User.my_subscribers), subqueryload(User.my_subscriptions)
            )
        )
        user = user_q.scalars().one()
        # Убедимся он ли это.
        assert user.id == main_user.id
        # Убедимся, что на него подписаны 2 пользователя.
        assert len(user.users_following_me) == 2
        assert {subscriber_1.id, subscriber_2.id} == set(
            subscriber.id for subscriber in user.users_following_me
        )


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


@pytest.mark.models
@pytest.mark.asyncio
async def test_add_attachment(db: Database) -> None:
    """
    Пробуем создать вложение.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        attachment = Attachment(image_path="Тут якобы путь к картинке")
        session.add(attachment)
        await session.commit()
        assert attachment.id

        # Пробуем привязать его к твиту.
        # Получаем пользователя.
        users_q = await session.execute(select(User).limit(1).order_by(User.id))
        users = users_q.scalars().all()
        main_user = users[0]
        # Создаём твит.
        tweet = Tweet(
            content="".join(choices(ascii_letters, k=MAX_TWEET_LENGTH - 1)),
            author=main_user,
        )
        tweet.attachments.append(attachment)
        session.add(tweet)
        await session.commit()

        # Ради чистоты теста достаём наше вложение из БД.
        session.expunge(attachment)
        attachment_q = await session.execute(
            select(Attachment).where(Attachment.id == attachment.id)
        )
        attachment_bd = attachment_q.scalars().one()
        assert attachment_bd.id == attachment.id
        # Проверим есть ли у вложения привязанный твит.
        assert attachment_bd.tweet_id
        assert attachment_bd.tweet == tweet


@pytest.mark.models
@pytest.mark.asyncio
async def test_delete_tweet(db: Database) -> None:
    """
    Ожидание: при удалении твита также удаляются вложения и лайки.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        users_q = await session.execute(select(User).order_by(User.id))
        user = users_q.scalars().first()
        assert user
        # Создаём твит с вложением и лайком.
        attachment, tweet, like = await create_attachment_tweet_like(session, user)
        attachment_id = attachment.id
        tweet_id = tweet.id
        like_id = like.id

        # Удаляем твит.
        await session.delete(tweet)
        await session.commit()
        # Убедимся, что твит удалён.
        tweet_q = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
        tweet_bd = tweet_q.scalars().one_or_none()
        assert not tweet_bd
        # Убедимся, что лайк удалён.
        like_q = await session.execute(select(Like).where(Like.id == like_id))
        like_bd = like_q.scalars().one_or_none()
        assert not like_bd
        # Убедимся, что вложение удалено.
        attachment_q = await session.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        attachment_bd = attachment_q.scalars().one_or_none()
        assert not attachment_bd


@pytest.mark.models
@pytest.mark.asyncio
async def test_delete_user(db: Database) -> None:
    """
    Ожидание: при удалении пользователя также удаляются все вложения и лайки и твиты.

    :param db: Database.
    :return: None.
    """
    async with db.get_sessionmaker() as session:
        users_q = await session.execute(select(User).order_by(User.id))
        user = users_q.scalars().first()
        assert user
        # Создаём твит с вложением и лайком.
        attachment, tweet, like = await create_attachment_tweet_like(session, user)
        attachment_id = attachment.id
        tweet_id = tweet.id
        like_id = like.id
        # Удаляем пользователя.
        await session.delete(user)
        await session.commit()

        # Убедимся, что твит удалён.
        tweet_q = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
        tweet_bd = tweet_q.scalars().one_or_none()
        assert not tweet_bd
        # Убедимся, что лайк удалён.
        like_q = await session.execute(select(Like).where(Like.id == like_id))
        like_bd = like_q.scalars().one_or_none()
        assert not like_bd
        # Убедимся, что вложение удалено.
        attachment_q = await session.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        attachment_bd = attachment_q.scalars().one_or_none()
        assert not attachment_bd
