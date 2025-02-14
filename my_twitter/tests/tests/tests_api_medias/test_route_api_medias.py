import os

import pytest
from app.database.database import Database
from app.database.models import Attachment
from app.settings.classes import Settings
from httpx import AsyncClient
from sqlalchemy import select


@pytest.mark.api_medias
@pytest.mark.asyncio
async def test_route_api_medias(
    client: AsyncClient,
    fake_image: dict[str, tuple[str, bytes, str]],
    db: Database,
    settings: Settings,
) -> None:
    """
    Тестируем роут /api/medias метод post.
    Так как мы не используем в приложении проверку содержимого файла через Pillow,
    то сойдёт фэйковый файл картинки, в противном случае этот тест провалится
    и нужно будет сюда передавать настоящую картинку.

    :param client: AsyncClient.
    :param fake_image: Словарь с данными тестового изображения для загрузки в тестах.
    :param db: Database.
    :param settings: Settings.
    :return: None.
    """
    client.headers.setdefault("api-key", "test")
    response = await client.post("/api/medias", files=fake_image)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    # Убедимся, что вложение создано.
    media_id = data["media_id"]
    async with db.get_sessionmaker() as session:
        attachment_q = await session.execute(
            select(Attachment).where(Attachment.id == media_id)
        )
        attachment = attachment_q.scalars().one_or_none()
    assert attachment
    # Убедимся, что файл сохранён.
    path = settings.MEDIA_FOLDER_ROOT / attachment.image_path
    assert os.path.exists(path)

    # Проверим создание вложения без вложения.
    response = await client.post("/api/medias")
    assert response.status_code != 200
