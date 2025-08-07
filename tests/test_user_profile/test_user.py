import pytest


@pytest.mark.asyncio
async def test_create_user(client, get_data_user):
    response = await client.post("/users/", json=get_data_user)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data and isinstance(data["id"], str)
    data_without_id = data.copy()
    data_without_id.pop("id", None)
    assert data_without_id == get_data_user
