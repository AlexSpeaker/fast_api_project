from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict

from app.database.database import Database


@dataclass
class Command:
    """
    Класс хранит информацию об исполняющей функции и описании этой функции.
    """
    exe_func: Callable[[Database], Coroutine[Any, Any, None]]
    description: str


class Commands:
    """
    Класс-регистратор команд.
    """

    def __init__(self) -> None:
        self.commands: Dict[str, Command] = {}

    def command(self, command_name: str, description: str) -> Callable[
        [Callable[[Database], Coroutine[Any, Any, None]]],
        Callable[[Database], Coroutine[Any, Any, None]],
    ]:
        """
        Функция-декоратор для регистрации команд.

        :param command_name: Название команды.
        :param description: Описание команды.
        :return: Декоратор.
        """

        def decorator(
            func: Callable[[Database], Coroutine[Any, Any, None]],
        ) -> Callable[[Database], Coroutine[Any, Any, None]]:
            """
            Регистрируем собранные функции с данными.

            :param func: Исполнительная функция.
            :return: Callable[[Database], Coroutine[Any, Any, None]].
            """
            self.commands[command_name] = Command(
                exe_func=func, description=description
            )
            return func

        return decorator
