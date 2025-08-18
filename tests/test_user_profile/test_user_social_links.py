import pytest

from tests.conftest import clear_cookies


@pytest.mark.asyncio
async def test_create_and_get_links_success(
    client, user_with_token, data_user_social_link
):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
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
async def test_get_links_empty_list_for_new_user(client, user_with_token):
    user_id = user_with_token["user_data"]["user_id"]
    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 200
    assert resp_get.json() == []


@pytest.mark.asyncio
async def test_create_link_unauthorized(client, user_with_token, data_user_social_link):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    clear_cookies(client)

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link
    )
    assert resp_create.status_code == 401


@pytest.mark.asyncio
async def test_create_link_wrong_user(
    client, two_users_with_tokens, data_user_social_link
):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]

    resp_create = await client.post(
        f"/users/{user2_id}/social-links",
        json=data_user_social_link,
        headers=user1_headers,
    )
    assert resp_create.status_code == 403


@pytest.mark.asyncio
async def test_create_link_for_nonexistent_user(
    client, user_with_token, data_user_social_link
):

    user_id = "00000000-0000-0000-0000-000000000000"
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 404
    assert "doesn't exist" in resp_create.json()["detail"]


@pytest.mark.asyncio
async def test_update_link_success(client, user_with_token, data_user_social_link):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    update_payload = {"id": link_id, "name": "NewName", "link": "https://example.com/me"}
    resp_update = await client.patch(
        f"/users/{user_id}/social-links/{link_id}", json=update_payload, headers=headers
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["name"] == update_payload["name"]
    assert updated["link"] == update_payload["link"]


@pytest.mark.asyncio
async def test_update_link_unauthorized(client, user_with_token, data_user_social_link):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    clear_cookies(client)

    update_payload = {"id": link_id, "name": "NewName", "link": "https://example.com/me"}
    resp_update = await client.patch(
        f"/users/{user_id}/social-links/{link_id}", json=update_payload
    )
    assert resp_update.status_code == 401


@pytest.mark.asyncio
async def test_update_link_wrong_user(
    client, two_users_with_tokens, data_user_social_link
):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]
    user2_headers = user2["headers"]

    resp_create = await client.post(
        f"/users/{user2_id}/social-links",
        json=data_user_social_link,
        headers=user2_headers,
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    update_payload = {
        "id": link_id,
        "name": "HackedName",
        "link": "https://example.com/hacked",
    }
    resp_update = await client.patch(
        f"/users/{user2_id}/social-links/{link_id}",
        json=update_payload,
        headers=user1_headers,
    )
    assert resp_update.status_code == 403


@pytest.mark.asyncio
async def test_update_link_validation_errors(
    client, user_with_token, data_user_social_link
):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    resp_update_empty = await client.patch(
        f"/users/{user_id}/social-links/{link_id}",
        json={"id": link_id, "name": "", "link": ""},
        headers=headers,
    )
    assert resp_update_empty.status_code == 422
    detail = resp_update_empty.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at least 1 character" in m for m in msgs)

    resp_update_long = await client.patch(
        f"/users/{user_id}/social-links/{link_id}",
        json={"id": link_id, "name": "a" * 51},
        headers=headers,
    )
    assert resp_update_long.status_code == 422
    detail = resp_update_long.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at most 50 characters" in m for m in msgs)


@pytest.mark.asyncio
async def test_delete_link_success(client, user_with_token, data_user_social_link):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    resp_delete = await client.delete(
        f"/users/{user_id}/social-links/{link_id}", headers=headers
    )
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 200
    links = resp_get.json()
    assert not any(link["id"] == link_id for link in links)


@pytest.mark.asyncio
async def test_delete_link_unauthorized(client, user_with_token, data_user_social_link):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    clear_cookies(client)

    resp_delete = await client.delete(f"/users/{user_id}/social-links/{link_id}")
    assert resp_delete.status_code == 401


@pytest.mark.asyncio
async def test_delete_link_wrong_user(
    client, two_users_with_tokens, data_user_social_link
):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]
    user2_headers = user2["headers"]

    resp_create = await client.post(
        f"/users/{user2_id}/social-links",
        json=data_user_social_link,
        headers=user2_headers,
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    resp_delete = await client.delete(
        f"/users/{user2_id}/social-links/{link_id}", headers=user1_headers
    )
    assert resp_delete.status_code == 403

    resp_get = await client.get(f"/users/{user2_id}/social-links")
    assert resp_get.status_code == 200
    links = resp_get.json()
    assert any(link["id"] == link_id for link in links)


@pytest.mark.asyncio
async def test_update_delete_nonexistent_link_404(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_update = await client.patch(
        f"/users/{user_id}/social-links/999999",
        json={"id": 999999, "name": "N"},
        headers=headers,
    )
    assert resp_update.status_code == 404

    resp_delete = await client.delete(
        f"/users/{user_id}/social-links/999999", headers=headers
    )
    assert resp_delete.status_code == 404


@pytest.mark.asyncio
async def test_get_links_for_nonexistent_user(client):

    user_id = "00000000-0000-0000-0000-000000000000"

    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 404
    assert "doesn't exist" in resp_get.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_manage_any_user_links(
    client, admin_with_token, user_with_token, data_user_social_link
):

    admin_headers = admin_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    user_headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=user_headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    update_payload = {
        "id": link_id,
        "name": "AdminUpdatedName",
        "link": "https://example.com/admin",
    }
    resp_update = await client.patch(
        f"/users/{user_id}/social-links/{link_id}",
        json=update_payload,
        headers=admin_headers,
    )
    assert resp_update.status_code == 200

    resp_delete = await client.delete(
        f"/users/{user_id}/social-links/{link_id}", headers=admin_headers
    )
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 200
    links = resp_get.json()
    assert not any(link["id"] == link_id for link in links)


@pytest.mark.asyncio
async def test_moderator_cannot_manage_other_user_links(
    client, moderator_with_token, user_with_token, data_user_social_link
):

    moderator_headers = moderator_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    user_headers = user_with_token["headers"]

    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=data_user_social_link, headers=user_headers
    )
    assert resp_create.status_code == 201
    link_id = resp_create.json()["id"]

    update_payload = {
        "id": link_id,
        "name": "ModeratorUpdatedName",
        "link": "https://example.com/moderator",
    }
    resp_update = await client.patch(
        f"/users/{user_id}/social-links/{link_id}",
        json=update_payload,
        headers=moderator_headers,
    )
    assert resp_update.status_code == 403

    resp_delete = await client.delete(
        f"/users/{user_id}/social-links/{link_id}", headers=moderator_headers
    )
    assert resp_delete.status_code == 403

    resp_get = await client.get(f"/users/{user_id}/social-links")
    assert resp_get.status_code == 200
    links = resp_get.json()
    link = next(link for link in links if link["id"] == link_id)
    assert link["name"] == data_user_social_link["name"]
    assert link["link"] == data_user_social_link["link"]


@pytest.mark.asyncio
async def test_social_link_validation_errors(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    empty_link = {"name": "", "link": ""}
    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=empty_link, headers=headers
    )
    assert resp_create.status_code == 422

    long_name = {"name": "a" * 51, "link": "https://example.com"}
    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=long_name, headers=headers
    )
    assert resp_create.status_code == 422

    long_link = {"name": "Test", "link": "a" * 256}
    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=long_link, headers=headers
    )
    assert resp_create.status_code == 422

    invalid_link = {"name": "Test", "link": "not-a-url"}
    resp_create = await client.post(
        f"/users/{user_id}/social-links", json=invalid_link, headers=headers
    )
    assert resp_create.status_code == 422
