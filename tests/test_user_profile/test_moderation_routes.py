import uuid

import pytest


@pytest.mark.asyncio
async def test_admin_get_users_forbidden_for_user(client, user_with_token):
    resp = await client.get("/admin/users", headers=user_with_token["headers"])
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_users_ok_for_admin(client, admin_with_token, user_with_token):
    resp = await client.get("/admin/users", headers=admin_with_token["headers"])
    assert resp.status_code == 200
    users = resp.json()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_get_moderators_and_admins_lists(client, admin_with_token, user_with_token):
    from jose import jwt

    from src.config import SECRET_KEY

    token_payload = jwt.decode(
        user_with_token["access_token"], SECRET_KEY, algorithms=["HS256"]
    )
    user_id = token_payload["sub"]

    promote = await client.post(
        f"/admin/users/{user_id}/promote",
        headers=admin_with_token["headers"],
    )
    assert promote.status_code == 200

    moderators = await client.get(
        "/admin/users/moderators", headers=admin_with_token["headers"]
    )
    assert moderators.status_code == 200
    emails = [u["email"] for u in moderators.json()]
    assert user_with_token["user_data"]["email"] in emails

    admins = await client.get("/admin/users/admins", headers=admin_with_token["headers"])
    assert admins.status_code == 200
    assert isinstance(admins.json(), list)


@pytest.mark.asyncio
async def test_promote_and_demote_permissions_and_errors(
    client, admin_with_token, user_with_token
):
    non_admin_try = await client.post(
        f"/admin/users/{uuid.uuid4()}/promote", headers=user_with_token["headers"]
    )
    assert non_admin_try.status_code == 403

    from jose import jwt

    from src.config import SECRET_KEY

    admin_token = admin_with_token["token"]
    admin_payload = jwt.decode(admin_token, SECRET_KEY, algorithms=["HS256"])
    admin_id = admin_payload["sub"]

    self_promote = await client.post(
        f"/admin/users/{admin_id}/promote", headers=admin_with_token["headers"]
    )
    assert self_promote.status_code == 400

    self_demote = await client.post(
        f"/admin/users/{admin_id}/demote", headers=admin_with_token["headers"]
    )
    assert self_demote.status_code == 400

    demote_404 = await client.post(
        f"/admin/users/{uuid.uuid4()}/demote", headers=admin_with_token["headers"]
    )
    assert demote_404.status_code == 404

    promote_404 = await client.post(
        f"/admin/users/{uuid.uuid4()}/promote", headers=admin_with_token["headers"]
    )
    assert promote_404.status_code == 404
