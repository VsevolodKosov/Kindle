import pytest


@pytest.mark.asyncio
async def test_second_login_revokes_previous_refresh(client, data_user_with_password):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201

    login1 = await client.post(
        "/auth/login",
        json={
            "email": data_user_with_password["email"],
            "password": data_user_with_password["password"],
        },
    )
    assert login1.status_code == 200
    rt1 = login1.json()["refresh_token"]

    login2 = await client.post(
        "/auth/login",
        json={
            "email": data_user_with_password["email"],
            "password": data_user_with_password["password"],
        },
    )
    assert login2.status_code == 200

    client.cookies.set("refresh_token", rt1)
    bad = await client.post("/auth/refresh")
    assert bad.status_code == 401
    assert bad.json()["detail"] == "Refresh token is not active"
