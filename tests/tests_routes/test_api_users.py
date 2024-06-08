import pytest


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_route_api_users_me_no_data(client):
    """
    Проверяем route api/users/me без api_key.
    При отсутствии данных всегда должен быть тестовый пользователь.
    Иначе ломается фронт.
    """
    response = await client.get("/api/users/me")
    assert response.status_code == 200
    assert "Александр5" in response.json()["user"]["name"]


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_route_api_users_me_with_data(client, other_users):
    """Проверяем route api/users/me с api_key"""
    client.headers.setdefault("api-key", other_users[0])
    response = await client.get("/api/users/me")
    assert response.status_code == 200
    assert "Александр7" in response.json()["user"]["name"]
    assert set(response.json()["user"].keys()) == {
        "id",
        "name",
        "followers",
        "following",
    }
    assert set(response.json().keys()) == {"result", "user"}


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_route_api_users_id(client):
    """Проверяем route api/users/<id>."""
    response = await client.get("/api/users/1")
    assert response.status_code == 200
    assert set(response.json()["user"].keys()) == {
        "id",
        "name",
        "followers",
        "following",
    }
    assert set(response.json().keys()) == {"result", "user"}


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_route_api_users_id_follow_post(client):
    """Проверяем route api/users/<id>/follow. Method POST (добавляем в подписки)."""
    response = await client.post("/api/users/3/follow")
    assert response.status_code == 200
    assert response.json()["result"]


@pytest.mark.api_users
@pytest.mark.asyncio
async def test_route_api_users_id_follow_delete(client):
    """Проверяем route api/users/<id>/follow. Method DELETE (удаляем из подписок)."""
    response = await client.delete("/api/users/1/follow")
    assert response.status_code == 200
    assert response.json()["result"]
