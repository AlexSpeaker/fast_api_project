from typing import List

from manage_utils.create_user import create_users
from my_twitter.app.database.database import DB


async def decision_center(sys_argv: List[str], db: DB):
    if len(sys_argv) == 1:
        print(
            "Используйте: python manage.py createuser [count: int].\n"
            "При использовании count, пользователи создадутся автоматически."
        )
    elif sys_argv[1] == "createuser":
        await create_users(db, sys_argv)
