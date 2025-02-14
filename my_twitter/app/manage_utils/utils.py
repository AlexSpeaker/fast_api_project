import re
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


def remove_backslash_sequences(text: str) -> str:
    r"""
    Удаляем все подстроки, начинающиеся с \ и продолжающиеся до пробела или конца строки.

    :param text: Текст.
    :return: Исправленный текст.
    """
    return re.sub(r"\\\S+", "", text)
