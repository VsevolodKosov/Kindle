import uuid

import pytest


@pytest.mark.asyncio
async def test_register_sets_cookies_and_returns_tokens(client, data_user_with_password):
    response = await client.post("/auth/register", json=data_user_with_password)
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body and "refresh_token" in body
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_sets_cookies(client, data_user_with_password):
    register = await client.post("/auth/register", json=data_user_with_password)
    assert register.status_code == 201

    login = await client.post(
        "/auth/login",
        json={
            "email": data_user_with_password["email"],
            "password": data_user_with_password["password"],
        },
    )
    assert login.status_code == 200
    assert "access_token" in login.cookies
    assert "refresh_token" in login.cookies


@pytest.mark.asyncio
async def test_me_requires_auth_401(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token_ok(client, user_with_token):
    headers = user_with_token["headers"]
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    me = response.json()
    assert me["email"] == user_with_token["user_data"]["email"]


@pytest.mark.asyncio
async def test_refresh_without_cookie_401(client, data_user_with_password):
    await client.post("/auth/register", json=data_user_with_password)
    client.cookies.pop("refresh_token", None)
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found in cookies"


@pytest.mark.asyncio
async def test_refresh_success_sets_new_cookies(client, data_user_with_password):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    refresh_token = reg.json()["refresh_token"]
    client.cookies.set("refresh_token", refresh_token)
    response = await client.post("/auth/refresh")
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body and "refresh_token" in body
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_401(client):
    client.cookies.set("refresh_token", "invalid.token.value")
    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found"


@pytest.mark.asyncio
async def test_revoke_without_cookie_401(client, data_user_with_password):
    await client.post("/auth/register", json=data_user_with_password)
    client.cookies.pop("refresh_token", None)
    response = await client.post("/auth/revoke")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found in cookies"


@pytest.mark.asyncio
async def test_revoke_and_then_refresh_is_inactive_401(client, data_user_with_password):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    refresh_token = reg.json()["refresh_token"]
    client.cookies.set("refresh_token", refresh_token)

    revoke = await client.post("/auth/revoke")
    assert revoke.status_code == 200
    assert revoke.json()["active"] is False

    client.cookies.set("refresh_token", refresh_token)
    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 401
    assert refresh_resp.json()["detail"] == "Refresh token is not active"


@pytest.mark.asyncio
async def test_logout_revokes_all_and_clears_cookies(client, user_with_token):
    headers = user_with_token["headers"]
    resp = await client.post("/auth/logout", headers=headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_auth_me_with_invalid_token_401(client):
    random_user_id = str(uuid.uuid4())
    from src.auth.utils import create_access_token

    token = create_access_token({"sub": random_user_id, "role": "user"})
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
