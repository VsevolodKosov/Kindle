import pytest


@pytest.mark.asyncio
async def test_me_with_broken_jwt_in_header_401(clean_client):
    resp = await clean_client.get(
        "/auth/me", headers={"Authorization": "Bearer xxx.yyy.zzz"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_deleted_user_token_401(client, user_with_token):
    user_id = user_with_token["user_data"]["user_id"]
    headers = user_with_token["headers"]
    del_resp = await client.delete(f"/users/{user_id}", headers=headers)
    assert del_resp.status_code == 204

    me = await client.get("/auth/me", headers=headers)
    assert me.status_code == 401
