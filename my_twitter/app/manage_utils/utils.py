from typing import Dict

from app.manage_utils.classes import Command


async def list_commands(commands: Dict[str, Command]) -> None:
    for command, data in commands.items():
        print(f"{command}: {data.description}")
