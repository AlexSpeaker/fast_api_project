import pytest
from httpx import AsyncClient


@pytest.mark.api_medias
@pytest.mark.asyncio
async def test_route_api_medias(
    client: AsyncClient, fake_image: dict[str, tuple[str, bytes, str]]
) -> None:
    """
    Тестируем роут /api/medias метод post.

    :param client: AsyncClient.
    :param fake_image: Словарь с данными тестового изображения для загрузки в тестах.
    :return: None.
    """
    client.headers.setdefault("api-key", "test")
    response = await client.post("/api/medias", files=fake_image)
    assert response.status_code == 200
