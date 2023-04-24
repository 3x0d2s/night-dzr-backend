from sqlalchemy import text
from conftest import AsyncClient, AsyncSessionLocal

# TODO: добавить тесты с невалидными данными
user_id: int = ...
token: str = ...


async def test_create_user(ac: AsyncClient):
    global user_id
    response = await ac.post(
        url="/auth/register",
        json={"email": "user@example.com",
              "password": "12345678",
              "name": "string",
              "surname": "string",
              "patronymic": "string",
              "phone_number": "89044464811"
              }
    )
    assert response.status_code == 201
    user_id = response.json()["id"]


async def test_auth(ac: AsyncClient):
    global token
    response = await ac.post(
        url="/auth/jwt/login",
        headers={"accept": "application/json",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "user@example.com", "password": "12345678"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]


async def test_get_user_by_token(ac: AsyncClient):
    response = await ac.get(
        url="/users/me",
        headers={"accept": "application/json",
                 "Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


async def test_get_user(ac: AsyncClient):
    async with AsyncSessionLocal() as session:
        await session.execute(text("UPDATE Users SET is_superuser=TRUE WHERE id=id"), {"id": user_id})
        await session.commit()
    response = await ac.get(
        url=f"/users/{user_id}",
        headers={"accept": "application/json",
                 "Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


async def test_delete_user(ac: AsyncClient):
    response = await ac.delete(
        url=f"/users/{user_id}",
        headers={"accept": "application/json",
                 "Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204
