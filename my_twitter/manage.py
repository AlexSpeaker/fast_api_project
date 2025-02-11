import asyncio
import sys

from app.manage_utils.decision_center import decision_center
from main import app


async def main() -> None:
    argv = sys.argv
    if argv:
        await decision_center(sys.argv[1], db=app.get_db())


if __name__ == "__main__":
    asyncio.run(main())
