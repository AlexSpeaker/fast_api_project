from random import choices
from string import ascii_letters

from app.database.database import Database
from app.database.models import Attachment, Like, User
from app.database.models.base import Base
from app.database.models.tweet import MAX_TWEET_LENGTH, Tweet
from sqlalchemy.ext.asyncio import AsyncSession


async def create_db(db: Database) -> None:
    """
    Создаёт все таблицы в базе данных.

    :param db: Экземпляр класса Database для работы с БД.
    :return: None.
    """
    async with db.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db(db: Database) -> None:
    """
    Удаляет все таблицы из базы данных.

    :param db: Экземпляр класса Database для работы с БД.
    :return: None.
    """
    async with db.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_users(db: Database) -> None:
    """
    Создаёт тестовых пользователей в базе данных.
    Генерирует 10 пользователей.

    :param db: Экземпляр класса Database для работы с БД.
    :return: None.
    """
    users = [
        User(
            first_name="".join(choices(ascii_letters, k=10)),
            surname="".join(choices(ascii_letters, k=10)),
            middle_name="".join(choices(ascii_letters, k=10)),
            api_key=f"test_{i:04d}",
        )
        for i in range(9)
    ]
    users.append(
        User(
            first_name="".join(choices(ascii_letters, k=10)),
            surname="".join(choices(ascii_letters, k=10)),
            middle_name="".join(choices(ascii_letters, k=10)),
            api_key="test",
        )
    )
    async with db.get_sessionmaker() as session:
        session.add_all(users)
        await session.commit()


async def create_attachment_tweet_like(
    session: AsyncSession, user: User
) -> tuple[Attachment, Tweet, Like]:
    """
    Функция создаёт твит с вложением и лайком.

    :param session: AsyncSession.
    :param user: Пользователь.
    :return: tuple[Attachment, Tweet, Like]
    """
    # Создадим вложение.
    attachment = Attachment(image_path="Тут якобы путь к картинке")
    session.add(attachment)
    await session.commit()
    assert attachment.id

    # Создадим твит с вложением.
    tweet = Tweet(
        content="".join(choices(ascii_letters, k=MAX_TWEET_LENGTH - 1)),
        author=user,
    )
    tweet.attachments.append(attachment)
    session.add(tweet)
    await session.commit()
    assert tweet.id

    # Лайкнем твит.
    like = Like(user=user, tweet=tweet)
    session.add(like)
    await session.commit()
    assert like.id
    return attachment, tweet, like
