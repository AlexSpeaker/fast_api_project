from typing import Dict, List

from manage_utils.utils import UserCreator, collection_of_information
from my_twitter.app.database.database import DB
from my_twitter.app.database.models import ApiKey, User


async def create_user_one(db: DB, user_data: Dict[str, str]):
    user: UserCreator = UserCreator(**user_data)
    user.set_db(db)
    await user.create_user()


async def create_users_auto(db: DB, count: int):
    print("Создаю пользователей...")
    session = db.get_session()
    start_index = 1
    users = [
        User(
            first_name=f"Александр{index}",
            middle_name=f"Сергеевич{index}",
            surname=f"Пушкин{index}",
            login=ApiKey(key=f"test{index}"),
        )
        for index in range(start_index, start_index + count)
    ]

    session.add_all(users)
    await session.commit()
    keys = "\n".join([user.login.key for user in users])
    print("OK.")
    print("Список api keys:")
    print(keys)


async def create_users(db: DB, sys_argv: List[str]):
    if len(sys_argv) == 2:
        user_data = collection_of_information()
        await create_user_one(db, user_data)
    elif len(sys_argv) == 3:
        count = int(sys_argv[2])
        await create_users_auto(db, count)
