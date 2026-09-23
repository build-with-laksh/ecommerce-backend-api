import pytest

@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post(
        "/users/register",
        json={
            "username":"TestUser123",
            "email": "testuser@gmail.com",
            "password": "Testuser123"
        }
    )

    assert response.status_code == 200
    assert response.json()["username"] == "TestUser123"
    assert response.json()["email"] == "testuser@gmail.com"
    assert "id" in response.json()
    assert "password" not in response.json()

@pytest.mark.anyio
async def test_login(client, user):
    response = await client.post(
        'users/login',
        data={
            "username": "TestingUser",
            "password": "testinguser@123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.anyio
async def test_me(token, client):
    response = await client.get(
        '/users/me',
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["username"] == "TestingUser"




