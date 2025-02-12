import asyncio
import sys

from app.manage_utils.decision_center import decision_center
from main import app
from main_debug import app_debug


async def main() -> None:
    argv = sys.argv
    if argv and len(argv) == 2:
        await decision_center(sys.argv[1], db=app.get_db())
    elif argv and len(argv) == 3 and argv[2] == "--debug":
        await decision_center(sys.argv[1], db=app_debug.get_db())


if __name__ == "__main__":
    asyncio.run(main())
