from conftest import AsyncClient

# TODO: добавить тесты с невалидными данными
user_id: int = ...
token: str = ...


async def test_create_user(ac: AsyncClient):
    global user_id
    response = await ac.post(
        url="/api/users",
        json={"name": "string",
              "surname": "string",
              "patronymic": "string",
              "email": "user@example.com",
              "phone_number": "stringstrin",
              "password": "string"
              }
    )
    assert response.status_code == 201
    user_id = response.json()["id"]


async def test_auth(ac: AsyncClient):
    global token
    response = await ac.post(
        url="/token",
        headers={"accept": "application/json",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "user@example.com", "password": "string"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]


async def test_get_user_by_token(ac: AsyncClient):
    response = await ac.get(
        url="/api/users/me/",
        headers={"accept": "application/json",
                 "Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


async def test_get_user(ac: AsyncClient):
    global user_id
    response = await ac.get(
        url=f"/api/users?id={user_id}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200


async def test_delete_user(ac: AsyncClient):
    global user_id
    response = await ac.delete(
        url=f"/api/users?id={user_id}",
        headers={"accept": "application/json"}
    )
    assert response.status_code == 200
