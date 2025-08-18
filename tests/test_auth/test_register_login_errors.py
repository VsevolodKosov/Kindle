import pytest


@pytest.mark.asyncio
async def test_register_duplicate_email_400(client, data_user_with_password):
    r1 = await client.post("/auth/register", json=data_user_with_password)
    assert r1.status_code == 201
    r2 = await client.post("/auth/register", json=data_user_with_password)
    assert r2.status_code == 400
    assert r2.json()["detail"] == "User with this email already exists"


@pytest.mark.asyncio
async def test_login_wrong_password_400(client, data_user_with_password):
    r1 = await client.post("/auth/register", json=data_user_with_password)
    assert r1.status_code == 201
    bad = await client.post(
        "/auth/login",
        json={
            "email": data_user_with_password["email"],
            "password": "WrongPass123!",
        },
    )
    assert bad.status_code == 400
    assert bad.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_revoke_already_revoked_token_401(client, data_user_with_password):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    rt = reg.json()["refresh_token"]
    client.cookies.set("refresh_token", rt)
    first = await client.post("/auth/revoke")
    assert first.status_code == 200

    client.cookies.set("refresh_token", rt)
    second = await client.post("/auth/revoke")
    assert second.status_code == 401
    assert second.json()["detail"] == "Refresh token is already revoked"
