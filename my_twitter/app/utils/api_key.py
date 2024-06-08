from typing import Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, subqueryload

from my_twitter.app.database.models import ApiKey, User


async def api_key_validator(
    api_key: Optional[str], session: AsyncSession, tweet=False
) -> User:
    """
    Функция проверит существование api_key в БД. Вернёт связанный объект User.
    При неудаче вернёт объект User тестового пользователя
    """
    _options = [
        subqueryload(User.my_subscriptions),
        subqueryload(User.my_subscribers),
        joinedload(User.login),
    ]
    if tweet:
        _options.append(subqueryload(User.tweets))
    user_q = await session.execute(
        select(User)
        .join(ApiKey)
        .where(
            or_(ApiKey.key == api_key, ApiKey.key == "test"), ApiKey.banned.is_(False)
        )
        .options(*_options)
    )
    users: Sequence[User] = user_q.scalars().all()
    if len(users) == 2 and users[1].login.key == api_key:
        return users[1]
    return users[0]
