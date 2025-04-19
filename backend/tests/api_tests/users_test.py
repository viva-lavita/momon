import pytest
from httpx import AsyncClient

from src.config import settings
from src.users.schemas import UserRegister


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        f"http://127.0.0.1:8000/api/v{settings.APP_VERSION}/users/signup",
        json=UserRegister(username="test_user", email="test@example.com", password="test_password").model_dump(),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test@example.com"
    new_user_id = response.json()["id"]

    response = await client.get(f"http://127.0.0.1:8000/api/v{settings.APP_VERSION}/users/{new_user_id}")
    assert response.status_code == 200
