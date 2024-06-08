import asyncio
import sys

from manage_utils.decision_center import decision_center
from my_twitter.main import db


async def main():
    await decision_center(sys.argv, db)


if __name__ == "__main__":
    s = asyncio.run(main())
