from uuid import uuid4

import pytest

@pytest.mark.asyncio
async def test_get_user(client, data_user):
    response_post = await client.post("/users/", json=data_user)
    assert response_post.status_code == 201
    user_id = response_post.json()["user_id"]

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 200
    body_get = response_get.json()
    assert "user_id" in body_get
    body_get.pop("user_id")
    assert body_get == data_user

@pytest.mark.asyncio
async def test__get_doesnt_exist_user(client):
    user_id = str(uuid4())
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 404
