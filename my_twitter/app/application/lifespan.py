import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.application.classes import CustomFastApi
from app.database.models.base import Base
from app.utils.utils import get_or_create_test_user


@asynccontextmanager
async def lifespan_func(app: CustomFastApi) -> AsyncGenerator[None, None]:
    """
    lifespan_func функция, обычно выполняет что-то до и после запуска приложения.
    В данной функции выполняется подключение к БД для создания таблиц, если таких ещё нет.
    А также создаёт тестового пользователя из-за особенности фронта.

    :param app: CustomFastApi.
    :return: AsyncGenerator[None, None].
    """
    timeout_task = 3.0
    loger = app.get_logger("lifespan")
    stop_event = asyncio.Event()  # Создаём флаг остановки

    async def db_connect() -> None:
        db = app.get_db()
        while not stop_event.is_set():  # Проверяем флаг остановки
            loger.info("Делаю попытку подключения к БД.")
            try:
                async with db.get_engine().begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            except ConnectionRefusedError:
                loger.warning(
                    f"Не удалось подключиться к БД! Повторная попытка через {timeout_task} сек."
                )
                await asyncio.sleep(timeout_task)
            else:
                loger.info("Успешное подключение к БД.")
                async with app.get_db().get_sessionmaker() as session:
                    await get_or_create_test_user(session, app.get_settings())
                break

    task = asyncio.create_task(db_connect())  # Запускаем процесс подключения

    try:
        loger.info("Запускаем приложение.")
        yield  # Запускаем приложение не дожидаясь выполнения db_connect().
    finally:
        stop_event.set()  # Ставим флаг остановки
        await task  # Дожидаемся завершения подключения к БД
        loger.info("Завершаю работу приложения.")
