import uuid

import pytest


@pytest.mark.asyncio
async def test_get_user_404(client):
    resp = await client.get(f"/users/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_user_404_and_empty_payload_400(client, user_with_token):
    resp_404 = await client.patch(
        f"/users/{uuid.uuid4()}", json={}, headers=user_with_token["headers"]
    )
    assert resp_404.status_code == 404

    user_id = user_with_token["user_data"]["user_id"]
    resp_400 = await client.patch(
        f"/users/{user_id}", json={}, headers=user_with_token["headers"]
    )
    assert resp_400.status_code == 400
    assert resp_400.json()["detail"] == "No data provided for update"


@pytest.mark.asyncio
async def test_delete_user_404(client, admin_with_token):
    resp = await client.delete(
        f"/users/{uuid.uuid4()}", headers=admin_with_token["headers"]
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_photos_and_links_user_not_found_on_create(
    client, user_with_token, data_user_photo, data_user_social_link
):
    headers = user_with_token["headers"]
    r1 = await client.post(
        f"/users/{uuid.uuid4()}/photos", json=data_user_photo, headers=headers
    )
    assert r1.status_code == 404
    r2 = await client.post(
        f"/users/{uuid.uuid4()}/social-links", json=data_user_social_link, headers=headers
    )
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_update_delete_non_exists_photo_and_link_404(
    client, user_with_token, data_user_photo, data_user_social_link
):
    headers = user_with_token["headers"]
    uid = user_with_token["user_data"]["user_id"]
    up_ph = await client.patch(
        f"/users/{uid}/photos/999999",
        json={"id": 999999, **data_user_photo},
        headers=headers,
    )
    assert up_ph.status_code == 404
    del_ph = await client.delete(f"/users/{uid}/photos/999999", headers=headers)
    assert del_ph.status_code == 404
    up_l = await client.patch(
        f"/users/{uid}/social-links/999999",
        json={"id": 999999, **data_user_social_link},
        headers=headers,
    )
    assert up_l.status_code == 404
    del_l = await client.delete(f"/users/{uid}/social-links/999999", headers=headers)
    assert del_l.status_code == 404


@pytest.mark.asyncio
async def test_patch_empty_payload_for_photo_and_link_400(client, user_with_token):
    headers = user_with_token["headers"]
    uid = user_with_token["user_data"]["user_id"]

    ph = await client.post(
        f"/users/{uid}/photos", json={"url": "https://example.com/a.jpg"}, headers=headers
    )
    assert ph.status_code == 201
    ph_id = ph.json()["id"]
    lk = await client.post(
        f"/users/{uid}/social-links",
        json={"name": "GitHub", "link": "https://github.com"},
        headers=headers,
    )
    assert lk.status_code == 201
    lk_id = lk.json()["id"]

    up_ph = await client.patch(
        f"/users/{uid}/photos/{ph_id}", json={"id": ph_id}, headers=headers
    )
    assert up_ph.status_code == 400
    assert up_ph.json()["detail"] == "No data provided for update"

    up_lk = await client.patch(
        f"/users/{uid}/social-links/{lk_id}", json={"id": lk_id}, headers=headers
    )
    assert up_lk.status_code == 400
    assert up_lk.json()["detail"] == "No data provided for update"


@pytest.mark.asyncio
async def test_get_all_photos_and_links_empty_lists(client, user_with_token):
    uid = user_with_token["user_data"]["user_id"]
    ph = await client.get(f"/users/{uid}/photos")
    assert ph.status_code == 200
    assert ph.json() == []
    lk = await client.get(f"/users/{uid}/social-links")
    assert lk.status_code == 200
    assert lk.json() == []


@pytest.mark.asyncio
async def test_update_and_delete_photo_and_link_success(client, user_with_token):
    headers = user_with_token["headers"]
    uid = user_with_token["user_data"]["user_id"]

    # Create
    ph = await client.post(
        f"/users/{uid}/photos", json={"url": "https://example.com/a.jpg"}, headers=headers
    )
    assert ph.status_code == 201
    ph_id = ph.json()["id"]
    lk = await client.post(
        f"/users/{uid}/social-links",
        json={"name": "Site", "link": "https://example.com"},
        headers=headers,
    )
    assert lk.status_code == 201
    lk_id = lk.json()["id"]

    # Update
    up_ph = await client.patch(
        f"/users/{uid}/photos/{ph_id}",
        json={"id": ph_id, "url": "https://example.com/b.jpg"},
        headers=headers,
    )
    assert up_ph.status_code == 200
    assert up_ph.json()["url"].endswith("b.jpg")

    up_lk = await client.patch(
        f"/users/{uid}/social-links/{lk_id}",
        json={"id": lk_id, "name": "Blog", "link": "https://blog.example.com"},
        headers=headers,
    )
    assert up_lk.status_code == 200
    assert up_lk.json()["name"] == "Blog"

    del_ph = await client.delete(f"/users/{uid}/photos/{ph_id}", headers=headers)
    assert del_ph.status_code == 204

    del_lk = await client.delete(f"/users/{uid}/social-links/{lk_id}", headers=headers)
    assert del_lk.status_code == 204
