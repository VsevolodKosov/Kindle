from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_user(client, data_user):
    response_post = await client.post("/users/", json=data_user)
    assert response_post.status_code == 201
    user_id = response_post.json()["user_id"]

    response_delete = await client.delete(f"/users/{user_id}")
    assert response_delete.status_code == 204

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_delete_doesnt_exist_user(client):
    user_id = str(uuid4())
    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 404
