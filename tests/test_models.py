from typing import Sequence

import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload, subqueryload

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import (
    ApiKey,
    Attachment,
    Like,
    Subscriptions,
    Tweet,
    User,
)


@pytest.mark.asyncio
async def test_create_user(db: DB):
    """Проверяем модель. Создаём юзера"""
    user: User = User(
        first_name="Александр", middle_name="Анатольевич", surname="Соколов"
    )
    async with db.get_session() as session:
        session.add(user)
        await session.commit()
    assert user.id


@pytest.mark.asyncio
async def test_create_user_with_key(db: DB):
    """Проверяем модель. Создаём вместе с ключом"""
    api_key = "112233445566"
    user: User = User(
        first_name="Александр",
        middle_name="Анатольевич",
        surname="Соколов",
        login=ApiKey(key=api_key),
    )
    async with db.get_session() as session:
        session.add(user)
        await session.commit()
        assert user.id

        key_q = await session.execute(select(ApiKey).where(ApiKey.user_id == user.id))
        key_obj: ApiKey = key_q.scalars().one()
    assert api_key == key_obj.key


@pytest.mark.asyncio
async def test_add_key_user(db: DB):
    """Проверяем модель. Добавляем ключ существующему пользователю"""
    api_key = "112233445566"
    async with db.get_session() as session:
        user_q = await session.execute(
            select(User).where(User.id == 1).options(joinedload(User.login))
        )

        user_obj: User = user_q.scalars().one()
        api_key_obj: ApiKey = ApiKey(key=api_key)
        user_obj.login = api_key_obj
        await session.commit()
    assert api_key_obj.id


@pytest.mark.asyncio
async def test_add_to_subscriptions_part_1(db: DB):
    """Проверяем модель. Добавляем в подписки при создании юзера."""
    async with db.get_session() as session:
        users_q = await session.execute(select(User))
        users: Sequence[User] = users_q.scalars().all()
        user = User(
            first_name="Александр",
            middle_name="Анатольевич",
            surname="Соколов",
            users_in_my_subscriptions=users,
        )
        session.add(user)
        await session.commit()

        users_in_my_subscriptions_q = await session.execute(
            select(Subscriptions).where(Subscriptions.user_id == user.id)
        )
        users_in_my_subscriptions = users_in_my_subscriptions_q.scalars().all()
    assert len(users_in_my_subscriptions) == 10


@pytest.mark.asyncio
async def test_add_to_subscriptions_part_2(db: DB):
    """Проверяем модель. Добавляем в подписки после создания юзера."""
    async with db.get_session() as session:
        user_q = await session.execute(
            select(User)
            .where(User.id == 1)
            .options(
                subqueryload(User.my_subscriptions), subqueryload(User.my_subscribers)
            )
        )
        user = user_q.scalars().one()

        users_q = await session.execute(select(User).where(User.id != user.id))
        users: Sequence[User] = users_q.scalars().all()

        user.users_in_my_subscriptions.extend(users)
        await session.commit()

        users_in_my_subscriptions_q = await session.execute(
            select(Subscriptions).where(Subscriptions.user_id == user.id)
        )
        users_in_my_subscriptions = users_in_my_subscriptions_q.scalars().all()
    assert len(users_in_my_subscriptions) == 9


@pytest.mark.asyncio
async def test_my_subscribers(db: DB):
    """Проверяем модель. Смотрим подписчиков."""
    async with db.get_session() as session:
        users_q = await session.execute(
            select(User).options(
                subqueryload(User.my_subscriptions), subqueryload(User.my_subscribers)
            )
        )
        users: Sequence[User] = users_q.scalars().all()
        users[9].users_in_my_subscriptions.extend(users[:8])
        await session.commit()
    name: str = users[9].first_name
    assert len(users[1].users_following_me) == 1
    assert users[1].users_following_me[0].id == users[9].id
    assert users[1].users_following_me[0].first_name == name


@pytest.mark.asyncio
async def test_create_tweet(db: DB):
    """Проверяем модель. Добавляем Tweet."""
    async with db.get_session() as session:
        user_q = await session.execute(
            select(User).where(User.id == 1).options(subqueryload(User.tweets))
        )
        user: User = user_q.scalars().one()
        tweet = Tweet(content="Content")
        user.tweets.append(tweet)
        await session.commit()
    assert tweet.id


@pytest.mark.asyncio
async def test_create_tweet_attachment(db: DB):
    """Проверяем модель. Добавляем Tweet c вложениями."""
    async with db.get_session() as session:
        user_q = await session.execute(
            select(User).where(User.id == 4).options(subqueryload(User.tweets))
        )
        user: User = user_q.scalars().one()
        attachment_1 = Attachment(image_url="/images/1.png")
        attachment_2 = Attachment(image_url="/images/2.png")
        attachments = [
            attachment_1,
            attachment_2,
        ]
        tweet = Tweet(
            content="Content",
            attachments=attachments,
        )
        user.tweets.append(tweet)
        await session.commit()
    assert attachment_1.id
    assert attachment_2.id


@pytest.mark.asyncio
async def test_create_like(db: DB):
    """Проверяем модель. Добавляем Like твиту."""
    async with db.get_session() as session:
        user_q = await session.execute(
            select(User).where(User.id == 10).options(subqueryload(User.likes))
        )
        user: User = user_q.scalars().one()

        tweet_q = await session.execute(select(Tweet).where(Tweet.id == 1))
        tweet: Tweet = tweet_q.scalars().one()
        like = Like(user_id=user.id, tweet_id=tweet.id)
        user.likes.append(like)
        await session.commit()
    assert like.id
