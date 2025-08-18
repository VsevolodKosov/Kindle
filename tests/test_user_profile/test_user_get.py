from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_get_user_success(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    body_get = response.json()
    assert "user_id" in body_get
    assert body_get["user_id"] == user_id
    assert body_get["email"] == user_data["email"]
    assert body_get["name"] == user_data["name"]
    assert body_get["surname"] == user_data["surname"]


@pytest.mark.asyncio
async def test_get_user_doesnt_exist(client):

    user_id = str(uuid4())
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 404
    assert "doesn't exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_unauthorized_access(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_invalid_uuid_format(client):

    invalid_user_id = "invalid-uuid-format"
    response = await client.get(f"/users/{invalid_user_id}")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_cross_user_access(client, two_users_with_tokens):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user1_id = user1["user_data"]["user_id"]
    user2_id = user2["user_data"]["user_id"]

    response = await client.get(f"/users/{user2_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == user2_id
    assert body["email"] == user2["user_data"]["email"]

    response = await client.get(f"/users/{user1_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == user1_id
    assert body["email"] == user1["user_data"]["email"]
