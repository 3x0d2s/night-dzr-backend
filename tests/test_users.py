from conftest import AsyncClient


async def test_create_user(ac: AsyncClient):
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


async def test_auth_and_get_me(ac: AsyncClient):
    response = await ac.post(
        url="/token",
        headers={"accept": "application/json",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "user@example.com", "password": "string"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = await ac.get(
        url="/api/users/me/",
        headers={"accept": "application/json",
                 "Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
