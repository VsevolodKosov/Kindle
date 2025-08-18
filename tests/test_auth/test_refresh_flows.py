import pytest


@pytest.mark.asyncio
async def test_refresh_twice_rotates_tokens_and_revokes_old(
    client, data_user_with_password
):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    rt1 = reg.json()["refresh_token"]

    client.cookies.set("refresh_token", rt1)
    ref1 = await client.post("/auth/refresh")
    assert ref1.status_code == 200
    rt2 = ref1.json()["refresh_token"]
    assert rt2 != rt1

    client.cookies.set("refresh_token", rt2)
    ref2 = await client.post("/auth/refresh")
    assert ref2.status_code == 200
    rt3 = ref2.json()["refresh_token"]
    assert rt3 not in {rt1, rt2}

    for old in [rt1, rt2]:
        client.cookies.set("refresh_token", old)
        bad = await client.post("/auth/refresh")
        assert bad.status_code == 401
        assert bad.json()["detail"] == "Refresh token is not active"


@pytest.mark.asyncio
async def test_refresh_invalid_jwt_but_present_in_db(
    client, data_user_with_password, test_db_async_session
):
    reg = await client.post("/auth/register", json=data_user_with_password)
    assert reg.status_code == 201
    valid_rt = reg.json()["refresh_token"]

    from sqlalchemy import update

    from src.auth.models import RefreshToken

    await test_db_async_session.execute(
        update(RefreshToken)
        .where(RefreshToken.token == valid_rt)
        .values(token="invalid.token.value")
    )
    await test_db_async_session.commit()

    client.cookies.set("refresh_token", "invalid.token.value")
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_preserves_admin_role(client, test_db_async_session):
    from jose import jwt
    from sqlalchemy import update

    from src.config import SECRET_KEY
    from src.user_profile.models import User

    data = {
        "email": "admin_role_check@mail.com",
        "name": "Admin",
        "surname": "User",
        "date_of_birth": "1980-01-01",
        "bio": "An admin user",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
        "password": "AdminPass123!",
    }
    reg = await client.post("/auth/register", json=data)
    assert reg.status_code == 201
    access_token = reg.json()["access_token"]
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload["sub"]

    await test_db_async_session.execute(
        update(User).where(User.id == user_id).values(role="admin")
    )
    await test_db_async_session.commit()

    login = await client.post(
        "/auth/login", json={"email": data["email"], "password": data["password"]}
    )
    assert login.status_code == 200
    assert "refresh_token" in client.cookies

    ref = await client.post("/auth/refresh")
    assert ref.status_code == 200
    new_access = ref.json()["access_token"]

    check_headers = {"Authorization": f"Bearer {new_access}"}
    client.cookies.clear()
    resp = await client.get("/admin/users", headers=check_headers)
    assert resp.status_code == 200
