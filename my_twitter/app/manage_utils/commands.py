from app.database.database import Database
from app.database.models import User
from app.manage_utils.classes import Commands
from app.manage_utils.utils import remove_backslash_sequences
from app.utils.utils import get_or_create

command_reg = Commands()


@command_reg.command(
    command_name="createuser", description="Создание нового пользователя."
)
async def create_user(db: Database) -> None:
    """
    Функция-команда для manage.py.
    Создаёт нового пользователя.

    :return: None.
    """
    print(
        "ВНИМАНИЕ! Данный метод рассчитывает, "
        "что информацию вводит человек, который знает, что он делает, "
        "поэтому никаких проверок или ограничений на ввод нет."
    )
    first_name = remove_backslash_sequences(input("Ведите ИМЯ пользователя: "))
    middle_name = remove_backslash_sequences(input("Ведите ОТЧЕСТВО пользователя: "))
    surname = remove_backslash_sequences(input("Ведите ФАМИЛИЮ пользователя: "))
    api_key = remove_backslash_sequences(input("Ведите API-KEY пользователя: "))
    choice_user = remove_backslash_sequences(
        input("Вы действительно хотите создать пользователя? Y/n: ")
    )
    if (
        choice_user.lower() == "n"
        or choice_user.lower() == "no"
        or choice_user.lower() == "тщ"
        or choice_user.lower() == "т"
    ):
        return
    async with db.get_sessionmaker() as session:
        created, user = await get_or_create(
            session,
            User,
            dict(
                first_name=first_name,
                middle_name=middle_name,
                surname=surname,
                api_key=api_key,
            ),
        )
        if created:
            print(
                f"Пользователь: {user.first_name} {user.middle_name} {user.surname}, "
                f"с api-key: {user.api_key}, был успешно создан."
            )
        else:
            print(
                f"Пользователь: {user.first_name} {user.middle_name} {user.surname}, "
                f"с api-key: {user.api_key}, уже есть в БД."
            )
