import pytest
from app.database.database import Database
from app.database.models import Attachment, Like, Tweet, User
from sqlalchemy import select
from tests.utils import create_attachment_tweet_like


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
        session.expunge(attachment)
        session.expunge(tweet)
        session.expunge(like)

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
