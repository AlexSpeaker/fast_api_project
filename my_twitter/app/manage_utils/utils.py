from typing import Dict

from app.manage_utils.classes import Command


async def list_commands(commands: Dict[str, Command]) -> None:
    """
    Функция выведет на экран все доступные команды.

    :param commands: Словарь команд.
    :return: None.
    """
    for command, data in commands.items():
        print(f"{command}: {data.description}")
