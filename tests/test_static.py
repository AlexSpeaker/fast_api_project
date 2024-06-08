import pytest


@pytest.mark.asyncio
async def test_index(client):
    """Проверяем статический index.html."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


@pytest.mark.asyncio
async def test_favicon(client):
    """Проверяем иконку favicon.ico."""
    response = await client.get("/favicon.ico")
    assert response.status_code == 200
