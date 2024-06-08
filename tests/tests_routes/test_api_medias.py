import os.path

import pytest

from tests.settings import TEST_DIR_INFO


@pytest.mark.api_medias
@pytest.mark.asyncio
async def test_route_api_medias_small_file_img(client, small_file_img, other_users, db):
    """Проверяем route /api/medias. Файл валидный."""
    client.headers.setdefault("api-key", other_users[0])
    data = {"file": ("image.png", small_file_img, "image/png")}
    response = await client.post("/api/medias", files=data)
    assert response.status_code == 200
    test_path = os.path.join(TEST_DIR_INFO["BASE_DIR_MEDIA"], other_users[0])
    assert os.path.isdir(test_path)
    assert response.json()["media_id"]


@pytest.mark.api_medias
@pytest.mark.asyncio
async def test_route_api_medias_big_file_img(client, big_file_img, other_users):
    """Проверяем route /api/medias. Файл не валидный."""
    client.headers.setdefault("api-key", other_users[0])
    data = {"file": ("image.png", big_file_img, "image/png")}
    response = await client.post("/api/medias", files=data)
    test_path = os.path.join(TEST_DIR_INFO["BASE_DIR_MEDIA"], other_users[0])
    assert response.status_code != 200
    assert not os.path.isdir(test_path)
