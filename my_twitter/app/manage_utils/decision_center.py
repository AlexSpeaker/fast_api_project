from app.database.database import Database
from app.manage_utils.commands import command_reg
from app.manage_utils.utils import list_commands


async def decision_center(command: str, db: Database) -> None:

    if command.lower() == "help":
        print("Список команд:")
        await list_commands(command_reg.commands)
        return

    data_command = command_reg.commands.get(command)
    if not data_command:
        print("Неизвестная команда.")
        return
    await data_command.exe_func(db)
