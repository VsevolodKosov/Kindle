import pytest

from tests.conftest import clear_cookies


@pytest.mark.asyncio
async def test_create_and_get_photos_success(client, user_with_token, data_user_photo):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo = resp_create_photo.json()
    assert photo["user_id"] == user_id
    assert photo["url"] == data_user_photo["url"]

    resp_get_photos = await client.get(f"/users/{user_id}/photos")
    assert resp_get_photos.status_code == 200
    photos = resp_get_photos.json()
    assert isinstance(photos, list)
    assert any(p["id"] == photo["id"] for p in photos)


@pytest.mark.asyncio
async def test_get_photos_empty_list_for_new_user(client, user_with_token):
    user_id = user_with_token["user_data"]["user_id"]
    resp = await client.get(f"/users/{user_id}/photos")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_update_photo_no_data_400(client, user_with_token, data_user_photo):
    user_id = user_with_token["user_data"]["user_id"]
    headers = user_with_token["headers"]
    created = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert created.status_code == 201
    photo_id = created.json()["id"]
    resp = await client.patch(
        f"/users/{user_id}/photos/{photo_id}", json={"id": photo_id}, headers=headers
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "No data provided for update"


@pytest.mark.asyncio
async def test_update_nonexistent_photo_404(client, user_with_token):
    user_id = user_with_token["user_data"]["user_id"]
    headers = user_with_token["headers"]
    resp = await client.patch(
        f"/users/{user_id}/photos/999999",
        json={"id": 999999, "url": "https://x"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_photo_unauthorized(client, user_with_token, data_user_photo):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    clear_cookies(client)

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo
    )
    assert resp_create_photo.status_code == 401


@pytest.mark.asyncio
async def test_create_photo_wrong_user(client, two_users_with_tokens, data_user_photo):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]

    resp_create_photo = await client.post(
        f"/users/{user2_id}/photos", json=data_user_photo, headers=user1_headers
    )
    assert resp_create_photo.status_code == 403


@pytest.mark.asyncio
async def test_create_photo_for_nonexistent_user(
    client, user_with_token, data_user_photo
):

    user_id = "00000000-0000-0000-0000-000000000000"
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 404
    assert "doesn't exist" in resp_create_photo.json()["detail"]


@pytest.mark.asyncio
async def test_update_photo_success(client, user_with_token, data_user_photo):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    update_payload = {"id": photo_id, "url": "https://example.com/new.jpg"}
    resp_update = await client.patch(
        f"/users/{user_id}/photos/{photo_id}", json=update_payload, headers=headers
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["url"] == update_payload["url"]

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    got_list = resp_get.json()
    assert any(
        p["id"] == photo_id and p["url"] == update_payload["url"] for p in got_list
    )


@pytest.mark.asyncio
async def test_update_photo_unauthorized(client, user_with_token, data_user_photo):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    clear_cookies(client)
    update_payload = {"id": photo_id, "url": "https://example.com/new.jpg"}
    resp_update = await client.patch(
        f"/users/{user_id}/photos/{photo_id}", json=update_payload
    )
    assert resp_update.status_code == 401


@pytest.mark.asyncio
async def test_update_photo_wrong_user(client, two_users_with_tokens, data_user_photo):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]
    user2_headers = user2["headers"]

    resp_create_photo = await client.post(
        f"/users/{user2_id}/photos", json=data_user_photo, headers=user2_headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    update_payload = {"id": photo_id, "url": "https://example.com/hacked.jpg"}
    resp_update = await client.patch(
        f"/users/{user2_id}/photos/{photo_id}", json=update_payload, headers=user1_headers
    )
    assert resp_update.status_code == 403


@pytest.mark.asyncio
async def test_update_photo_validation_errors(client, user_with_token, data_user_photo):
    """Тест валидационных ошибок при обновлении фото"""
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    resp_update_empty = await client.patch(
        f"/users/{user_id}/photos/{photo_id}",
        json={"id": photo_id, "url": ""},
        headers=headers,
    )
    assert resp_update_empty.status_code == 422
    detail = resp_update_empty.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at least 1 character" in m for m in msgs)

    too_long = "a" * 256
    resp_update_long = await client.patch(
        f"/users/{user_id}/photos/{photo_id}",
        json={"id": photo_id, "url": too_long},
        headers=headers,
    )
    assert resp_update_long.status_code == 422
    detail = resp_update_long.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at most 255 characters" in m for m in msgs)


@pytest.mark.asyncio
async def test_delete_photo_success(client, user_with_token, data_user_photo):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    resp_delete = await client.delete(
        f"/users/{user_id}/photos/{photo_id}", headers=headers
    )
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    photos = resp_get.json()
    assert not any(p["id"] == photo_id for p in photos)


@pytest.mark.asyncio
async def test_delete_photo_unauthorized(client, user_with_token, data_user_photo):
    """Тест удаления фото без авторизации"""
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    clear_cookies(client)
    resp_delete = await client.delete(f"/users/{user_id}/photos/{photo_id}")
    assert resp_delete.status_code == 401


@pytest.mark.asyncio
async def test_delete_photo_wrong_user(client, two_users_with_tokens, data_user_photo):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]
    user2_headers = user2["headers"]

    resp_create_photo = await client.post(
        f"/users/{user2_id}/photos", json=data_user_photo, headers=user2_headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    resp_delete = await client.delete(
        f"/users/{user2_id}/photos/{photo_id}", headers=user1_headers
    )
    assert resp_delete.status_code == 403

    resp_get = await client.get(f"/users/{user2_id}/photos")
    assert resp_get.status_code == 200
    photos = resp_get.json()
    assert any(p["id"] == photo_id for p in photos)


@pytest.mark.asyncio
async def test_delete_photo_doesnt_exist(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    photo_id = 999999
    resp_delete = await client.delete(
        f"/users/{user_id}/photos/{photo_id}", headers=headers
    )
    assert resp_delete.status_code == 404


@pytest.mark.asyncio
async def test_get_photos_for_nonexistent_user(client):

    user_id = "00000000-0000-0000-0000-000000000000"

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 404
    assert "doesn't exist" in resp_get.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_manage_any_user_photos(
    client, admin_with_token, user_with_token, data_user_photo
):

    admin_headers = admin_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    user_headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=user_headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    update_payload = {"id": photo_id, "url": "https://example.com/admin_updated.jpg"}
    resp_update = await client.patch(
        f"/users/{user_id}/photos/{photo_id}", json=update_payload, headers=admin_headers
    )
    assert resp_update.status_code == 200

    resp_delete = await client.delete(
        f"/users/{user_id}/photos/{photo_id}", headers=admin_headers
    )
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    photos = resp_get.json()
    assert not any(p["id"] == photo_id for p in photos)


@pytest.mark.asyncio
async def test_moderator_cannot_manage_other_user_photos(
    client, moderator_with_token, user_with_token, data_user_photo
):

    moderator_headers = moderator_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    user_headers = user_with_token["headers"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo, headers=user_headers
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    update_payload = {"id": photo_id, "url": "https://example.com/moderator_updated.jpg"}
    resp_update = await client.patch(
        f"/users/{user_id}/photos/{photo_id}",
        json=update_payload,
        headers=moderator_headers,
    )
    assert resp_update.status_code == 403

    resp_delete = await client.delete(
        f"/users/{user_id}/photos/{photo_id}", headers=moderator_headers
    )
    assert resp_delete.status_code == 403

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    photos = resp_get.json()
    photo = next(p for p in photos if p["id"] == photo_id)
    assert photo["url"] == data_user_photo["url"]
