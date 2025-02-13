from random import choices
from string import ascii_letters

from app.database.database import Database
from app.database.models import User
from app.database.models.base import Base


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
        for i in range(10)
    ]
    async with db.get_sessionmaker() as session:
        session.add_all(users)
        await session.commit()
