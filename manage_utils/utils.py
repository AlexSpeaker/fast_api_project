import re
from typing import Dict, Optional

from my_twitter.app.database.database import DB
from my_twitter.app.database.models import ApiKey, User


class UserCreatorError(Exception):
    pass


class UserCreator:
    _db = None

    def __init__(self, first_name, middle_name, surname, api_key):
        self.first_name = first_name
        self.middle_name = middle_name
        self.surname = surname
        self.api_key = api_key

    def set_db(self, db: DB):
        self._db = db

    async def create_user(self):
        session = self._db.get_session()
        if self._db is None:
            raise UserCreatorError("Не подключена БД")
        user = User(
            first_name=self.first_name,
            middle_name=self.middle_name,
            surname=self.surname,
            login=ApiKey(key=self.api_key),
        )
        session.add(user)
        await session.commit()


def collection_of_information() -> Dict[str, str]:
    print("Введите данные пользователя:")
    surname: Optional[str] = None
    first_name: Optional[str] = None
    api_key: Optional[str] = None
    while not surname:
        surname = input("Фамилия (поле не может быть пустым): ")
    while not first_name:
        first_name = input("Имя (поле не может быть пустым): ")
    middle_name = input("Отчество: ")
    while not api_key or len(api_key) < 4:
        api_key = input("api_key (поле не может быть пустым и меньше 4 символов): ")
        pattern = r"^test.*"
        if re.match(pattern, api_key):
            api_key = None
            print(
                "Ключи test или test1, test2, test3, ... testN зарезервированы, выберите другой api key"
            )
    return dict(
        surname=surname, first_name=first_name, middle_name=middle_name, api_key=api_key
    )
