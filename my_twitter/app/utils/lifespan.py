import sys
import time

from sqlalchemy import select

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import ApiKey, Base, User
from my_twitter.settings import DEBUG


def lifespan(db: DB):
    async def wrap_lifespan(*args, **kwargs):
        if not DEBUG:
            for _ in range(10):
                try:
                    async with db.engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                except ConnectionRefusedError:
                    time.sleep(2.0)
                else:
                    break
            else:
                sys.exit(1)
        else:
            async with db.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        async with db.get_session() as session:
            test_api_key_q = await session.execute(
                select(ApiKey).where(ApiKey.key == "test")
            )
            test_api_key = test_api_key_q.scalars().one_or_none()
            if not test_api_key:
                user = User(
                    first_name="Виктор",
                    middle_name="Петрович",
                    surname="Тест",
                    login=ApiKey(key="test"),
                )
                session.add(user)
                await session.commit()
        yield

    return wrap_lifespan
