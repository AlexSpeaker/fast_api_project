import asyncio
import os
import shutil

import pytest
from httpx import ASGITransport, AsyncClient

from my_twitter.app.app import AppCreator
from my_twitter.app.database.database import DB
from my_twitter.app.database.models import ApiKey, Base, Like, Tweet, User
from tests.settings import TEST_BASE_DIR, TEST_DIR_INFO


async def create_db(db: DB):
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db(db: DB):
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def default_user():
    return "test"


@pytest.fixture
def other_users():
    return "test11111", "test22222"


@pytest.fixture
def db(default_user, other_users):
    _db = DB("sqlite+aiosqlite://")
    asyncio.run(create_db(_db))
    session = _db.get_session()
    users = [
        User(
            first_name=f"Александр{i}",
            middle_name=f"Анатольевич{i}",
            surname=f"Соколов{i}",
        )
        for i in range(10)
    ]
    tweet = Tweet(content="Content")
    tweet.likes.append(Like(user=users[6]))
    users[5].login = ApiKey(key=default_user)
    users[5].users_in_my_subscriptions.append(users[0])
    users[7].login = ApiKey(key=other_users[0])
    users[7].tweets.append(tweet)
    users[6].login = ApiKey(key=other_users[1])
    session.add_all(users)
    asyncio.run(session.commit())
    yield _db
    asyncio.run(session.close())
    asyncio.run(_db.engine.dispose())
    asyncio.run(drop_db(_db))
    test_path = os.path.join(TEST_DIR_INFO["BASE_DIR_MEDIA"], other_users[0])
    if os.path.isdir(test_path):
        shutil.rmtree(test_path)


@pytest.fixture
def app(db):
    _app_c = AppCreator(db, dir_info=TEST_DIR_INFO)
    return _app_c.get_app


@pytest.fixture
def client(app):
    return AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    )


@pytest.fixture
def small_file_img():
    with open(
        os.path.join(
            TEST_BASE_DIR, "tests_routes", "files_for_testing", "small_img.png"
        ),
        "rb",
    ) as f:
        file = f.read()
    return file


@pytest.fixture
def big_file_img():
    with open(
        os.path.join(TEST_BASE_DIR, "tests_routes", "files_for_testing", "big_img.png"),
        "rb",
    ) as f:
        file = f.read()
    return file
