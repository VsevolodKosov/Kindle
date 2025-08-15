import pytest


@pytest.mark.asyncio
async def test_create_and_get_photos_success(client, data_user, data_user_photo):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo
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
async def test_update_photo_success(client, data_user, data_user_photo):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    update_payload = {"id": photo_id, "url": "https://example.com/new.jpg"}
    resp_update = await client.patch(
        f"/users/{user_id}/photos/{photo_id}", json=update_payload
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["url"] == update_payload["url"]

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    got_list = resp_get.json()
    assert any(
        p["id"] == photo_id and p["url"] == update_payload["url"]
        for p in got_list
    )


@pytest.mark.asyncio
async def test_update_photo_validation_errors(client, data_user, data_user_photo):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    # Пустая строка
    resp_update_empty = await client.patch(
        f"/users/{user_id}/photos/{photo_id}",
        json={"id": photo_id, "url": ""}
    )
    assert resp_update_empty.status_code == 422
    detail = resp_update_empty.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at least 1 character" in m for m in msgs)

    # Слишком длинная строка (>255)
    too_long = "a" * 256
    resp_update_long = await client.patch(
        f"/users/{user_id}/photos/{photo_id}",
        json={"id": photo_id, "url": too_long}
    )
    assert resp_update_long.status_code == 422
    detail = resp_update_long.json()["detail"]
    msgs = [e.get("msg", "") for e in detail] if isinstance(detail, list) else [detail]
    assert any("String should have at most 255 characters" in m for m in msgs)


@pytest.mark.asyncio
async def test_delete_photo_success(client, data_user, data_user_photo):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_create_photo = await client.post(
        f"/users/{user_id}/photos", json=data_user_photo
    )
    assert resp_create_photo.status_code == 201
    photo_id = resp_create_photo.json()["id"]

    resp_delete = await client.delete(f"/users/{user_id}/photos/{photo_id}")
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/users/{user_id}/photos")
    assert resp_get.status_code == 200
    assert all(p["id"] != photo_id for p in resp_get.json())


@pytest.mark.asyncio
async def test_update_delete_nonexistent_photo_404(client, data_user):
    resp_post_user = await client.post("/users/", json=data_user)
    assert resp_post_user.status_code == 201
    user_id = resp_post_user.json()["user_id"]

    resp_update = await client.patch(
        f"/users/{user_id}/photos/999999",
        json={"id": 999999, "url": "https://example.com/1.jpg"}
    )
    assert resp_update.status_code == 404

    resp_delete = await client.delete(f"/users/{user_id}/photos/999999")
    assert resp_delete.status_code == 404
