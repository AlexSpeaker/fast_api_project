import pytest
from app.database.database import Database
from app.database.models import User


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
