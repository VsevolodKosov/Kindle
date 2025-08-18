from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_user_success(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    response_delete = await client.delete(f"/users/{user_id}", headers=headers)
    assert response_delete.status_code == 204

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    from httpx import ASGITransport, AsyncClient

    from src.main import app

    transport = ASGITransport(app=app)
    clean_client = AsyncClient(
        transport=transport, base_url="http://testserver", cookies={}
    )

    try:

        response = await clean_client.delete(f"/users/{user_id}")
        assert response.status_code == 401
    finally:
        await clean_client.aclose()


@pytest.mark.asyncio
async def test_delete_user_wrong_user(client, two_users_with_tokens):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]

    response = await client.delete(f"/users/{user2_id}", headers=user1_headers)
    assert response.status_code == 403

    response_get = await client.get(f"/users/{user2_id}")
    assert response_get.status_code == 200


@pytest.mark.asyncio
async def test_delete_user_doesnt_exist(client, user_with_token):

    user_id = str(uuid4())
    headers = user_with_token["headers"]

    response = await client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 404
    assert "doesn't exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_user_invalid_uuid_format(client, user_with_token):

    invalid_user_id = "invalid-uuid-format"
    headers = user_with_token["headers"]

    response = await client.delete(f"/users/{invalid_user_id}", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_user_admin_can_delete_any_user(
    client, admin_with_token, user_with_token
):

    admin_headers = admin_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    response = await client.delete(f"/users/{user_id}", headers=admin_headers)
    assert response.status_code == 204

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_moderator_cannot_delete_other_user(
    client, moderator_with_token, user_with_token
):

    moderator_headers = moderator_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    response = await client.delete(f"/users/{user_id}", headers=moderator_headers)
    assert response.status_code == 403

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 200
