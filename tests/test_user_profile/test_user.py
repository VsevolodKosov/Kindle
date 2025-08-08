import pytest


@pytest.mark.asyncio
async def test_create_user(client, data_user):
    response = await client.post("/users/", json=data_user)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data and isinstance(data["id"], str)
    data_without_id = data.copy()
    data_without_id.pop("id", None)
    assert data_without_id == data_user


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, create_user, data_user):
    await create_user(data_user)
    response = await client.post("/users/", json=data_user)
    assert response.status_code == 400
    assert "email" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_empty_user(client):
    data = {}
    response = await client.post("/users/", json=data)
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "modifier, expected_status",
    [
        (lambda u: {}, 422),

        (lambda u: {**u, "username": ""}, 422),
        (lambda u: {**u, "username": "a" * 101}, 422),
        (lambda u: {k: v for k, v in u.items() if k != "username"}, 422),

        (lambda u: {**u, "email": ""}, 422),
        (lambda u: {**u, "email": "not-an-email"}, 422),
        (
            lambda u: {
                **u,
                "email": "a" * 256 + "@example.com"
            },
            422,
        ),
        (lambda u: {k: v for k, v in u.items() if k != "email"}, 422),

        (lambda u: {**u, "gender": ""}, 422),
        (lambda u: {**u, "gender": "x"}, 422),
        (lambda u: {**u, "gender": "x"}, 422),
        (lambda u: {k: v for k, v in u.items() if k != "gender"}, 422),

        (lambda u: {**u, "country": ""}, 422),
        (lambda u: {**u, "country": "a" * 101}, 422),
        (lambda u: {k: v for k, v in u.items() if k != "country"}, 422),

        (lambda u: {**u, "city": ""}, 422),
        (lambda u: {**u, "city": "a" * 101}, 422),
        (lambda u: {k: v for k, v in u.items() if k != "city"}, 422),

        (lambda u: {**u, "bio": "a" * 5001}, 422),

        (lambda u: {**u, "email": 12345}, 422),
        (lambda u: {**u, "gender": ["m"]}, 422),
        (lambda u: {**u, "country": {"name": "Russia"}}, 422),
    ]
)
async def test_create_user_invalid_data(client, data_user, modifier, expected_status):
    payload = modifier(data_user)
    response = await client.post("/users/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_user_success(client, create_user, data_user):
    created = await create_user(data_user)
    user_id = created["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    # Сравниваем UUID корректно
    assert str(data["id"]) == str(user_id)
    for key in data_user:
        assert data[key] == data_user[key]


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get("/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_success(client, create_user, data_user):
    created = await create_user(data_user)
    user_id = created["id"]

    update_data = {
        "username": "NewName",
        "bio": "Updated bio",
    }
    response = await client.patch(
    "/users/",
    json=update_data,
    params={"user_id": user_id},
)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["bio"] == update_data["bio"]


@pytest.mark.asyncio
async def test_update_user_email_duplicate(client, create_user, data_user):
    await create_user(data_user)
    user2_data = data_user.copy()
    user2_data["email"] = "different@example.com"
    user2 = await create_user(user2_data)

    response = await client.patch(
        "/users/",
        json={"email": data_user["email"]},
        params={"user_id": user2["id"]}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_success(client, create_user, data_user):
    created = await create_user(data_user)
    user_id = created["id"]

    response = await client.delete("/users/", params={"user_id": user_id})
    assert response.status_code == 200
    data = response.json()
    assert str(data["id"]) == str(user_id)

    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
