from random import choices
from string import ascii_letters

import pytest
from app.database.database import Database
from app.database.models import Attachment, Tweet, User
from app.database.models.tweet import MAX_TWEET_LENGTH
from sqlalchemy import select


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
