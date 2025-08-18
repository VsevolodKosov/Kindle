import pytest


@pytest.mark.asyncio
async def test_revoke_all_after_multiple_logins_returns_all(
    client, data_user_with_password
):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201

    for _ in range(2):
        login = await client.post(
            "/auth/login",
            json={
                "email": data_user_with_password["email"],
                "password": data_user_with_password["password"],
            },
        )
        assert login.status_code == 200

    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    resp = await client.post("/auth/logout", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_revoke_not_found_refresh_token_401(client):
    client.cookies.clear()
    client.cookies.set("refresh_token", "not.stored.token")
    resp = await client.post("/auth/revoke")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Refresh token not found"
