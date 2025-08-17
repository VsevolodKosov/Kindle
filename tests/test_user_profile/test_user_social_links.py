import pytest


@pytest.mark.asyncio
async def test_create_and_get_links_success(client, data_user, data_user_social_link):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link
    )
    assert resp_create.status_code == 201
    link_obj = resp_create.json()
    assert link_obj["user_id"] == user_id
    assert link_obj["name"] == data_user_social_link["name"]
    assert link_obj["link"] == data_user_social_link["link"]

    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 200
    links = resp_get.json()
    assert isinstance(links, list)
    assert any(link["id"] == link_obj["id"] for link in links)


@pytest.mark.asyncio
async def test_update_link_success(client, data_user, data_user_social_link):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    update_payload = {"id": link_id, "name": "NewName", "link": "https://example.com/me"}
    resp_update = await client.patch(
        f"/users/{user_id}/social-links/{link_id}", json=update_payload
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["name"] == update_payload["name"]
    assert updated["link"] == update_payload["link"]


@pytest.mark.asyncio
async def test_update_link_validation_errors(client, data_user, data_user_social_link):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    # Пустые строки
    resp_update_empty = await client.patch(
        f"/users/{user_id}/social-links/{link_id}",
        json={"id": link_id, "name": "", "link": ""},
    )
    assert resp_update_empty.status_code == 422
    detail = resp_update_empty.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at least 1 character" in m for m in msgs)
    assert any("String should have at least 1 character" in m for m in msgs)

    # Длинные значения
    resp_update_long = await client.patch(
        f"/users/{user_id}/social-links/{link_id}", json={"id": link_id, "name": "a" * 51}
    )
    assert resp_update_long.status_code == 422
    detail = resp_update_long.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at most 50 characters" in m for m in msgs)


@pytest.mark.asyncio
async def test_update_delete_nonexistent_link_404(client, data_user):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_update = await client.patch(
        f"/users/{user_id}/social-links/999999", json={"id": 999999, "name": "N"}
    )
    assert resp_update.status_code == 404

    resp_delete = await client.delete(f"/users/{user_id}/social-links/999999")
    assert resp_delete.status_code == 404
