import pytest

from tests.conftest import clear_cookies


@pytest.mark.asyncio
async def test_update_user_duplicate_email(client, two_users_with_tokens):
    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    first_user_id = user1["user_data"]["user_id"]
    second_user_id = user2["user_data"]["user_id"]
    second_user_headers = user2["headers"]

    update_payload = {"email": user1["user_data"]["email"]}
    response_update = await client.patch(
        f"/users/{second_user_id}", json=update_payload, headers=second_user_headers
    )

    assert response_update.status_code == 400
    error_detail = response_update.json()["detail"]
    assert "already exists" in error_detail

    response_get = await client.get(f"/users/{second_user_id}")
    assert response_get.status_code == 200
    user_data = response_get.json()
    assert user_data["email"] == user2["user_data"]["email"]

    response_get_first = await client.get(f"/users/{first_user_id}")
    assert response_get_first.status_code == 200
    first_user_data = response_get_first.json()
    assert first_user_data["email"] == user1["user_data"]["email"]


@pytest.mark.asyncio
async def test_update_user_unauthorized(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    clear_cookies(client)

    update_payload = {"name": "NewName"}
    response = await client.patch(f"/users/{user_id}", json=update_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_wrong_user(client, two_users_with_tokens):

    user1 = two_users_with_tokens["user1"]
    user2 = two_users_with_tokens["user2"]

    user2_id = user2["user_data"]["user_id"]
    user1_headers = user1["headers"]

    update_payload = {"name": "HackedName"}
    response = await client.patch(
        f"/users/{user2_id}", json=update_payload, headers=user1_headers
    )
    assert response.status_code == 403

    response_get = await client.get(f"/users/{user2_id}")
    assert response_get.status_code == 200
    user_data = response_get.json()
    assert user_data["name"] == user2["user_data"]["name"]


@pytest.mark.asyncio
async def test_update_user_admin_can_update_any_user(
    client, admin_with_token, user_with_token
):

    admin_headers = admin_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    update_payload = {"name": "AdminUpdatedName"}
    response = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=admin_headers
    )
    assert response.status_code == 200

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 200
    updated_user = response_get.json()
    assert updated_user["name"] == "AdminUpdatedName"


@pytest.mark.asyncio
async def test_update_user_moderator_cannot_update_other_user(
    client, moderator_with_token, user_with_token
):
    """Тест что модератор не может обновить другого пользователя"""
    moderator_headers = moderator_with_token["headers"]
    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]

    update_payload = {"name": "ModeratorUpdatedName"}
    response = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=moderator_headers
    )
    assert response.status_code == 403

    response_get = await client.get(f"/users/{user_id}")
    assert response_get.status_code == 200
    user_data_from_db = response_get.json()
    assert user_data_from_db["name"] == user_data["name"]


@pytest.mark.parametrize(
    "update_payload,expected_status,expected_error",
    [
        ({"email": "newemail@example.com"}, 200, None),
        ({"name": "NewName"}, 200, None),
        ({"surname": "NewSurname"}, 200, None),
        ({"date_of_birth": "1985-06-20"}, 200, None),
        ({"bio": "Новая биография пользователя"}, 200, None),
        ({"gender": "f"}, 200, None),
        ({"country": "Russia"}, 200, None),
        ({"city": "Moscow"}, 200, None),
        (
            {
                "name": "UpdatedName",
                "surname": "UpdatedSurname",
                "bio": "Обновленная биография",
            },
            200,
            None,
        ),
        (
            {
                "email": "multi@example.com",
                "country": "Germany",
                "city": "Berlin",
                "gender": "m",
            },
            200,
            None,
        ),
        ({"bio": None}, 200, None),
        ({"bio": "Восстановленная биография"}, 200, None),
        ({"email": "invalid-email"}, 422, "value is not a valid email address"),
        (
            {"email": "a" * 100 + "@example.com"},
            422,
            "value is not a valid email address",
        ),
        ({"email": ""}, 422, "value is not a valid email address"),
        ({"name": ""}, 422, "String should have at least 1 character"),
        ({"name": "   "}, 422, "String should have at least 1 character"),
        ({"name": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"surname": ""}, 422, "String should have at least 1 character"),
        ({"surname": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"date_of_birth": "invalid-date"}, 422, "Input should be a valid date"),
        ({"gender": "x"}, 422, "Gender must be 'm' or 'f'"),
        ({"gender": "mm"}, 422, "String should have at most 1 character"),
        ({"gender": "M"}, 422, "Gender must be 'm' or 'f'"),
        ({"gender": "male"}, 422, "String should have at most 1 character"),
        ({"gender": ""}, 422, "String should have at least 1 character"),
        ({"country": ""}, 422, "String should have at least 1 character"),
        ({"country": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"city": ""}, 422, "String should have at least 1 character"),
        ({"city": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"email": 123}, 422, "Input should be a valid string"),
        ({"name": 123}, 422, "Input should be a valid string"),
        ({"surname": True}, 422, "Input should be a valid string"),
        ({"gender": 123}, 422, "Input should be a valid string"),
        ({"country": ["Russia"]}, 422, "Input should be a valid string"),
        ({"city": {"city": "Moscow"}}, 422, "Input should be a valid string"),
        ({}, 400, "No data provided for update"),
        ({"name": "a" * 50}, 200, None),
        ({"bio": "a" * 5000}, 200, None),
        ({"date_of_birth": "2006-08-15"}, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_update_user_comprehensive(
    client, user_with_token, update_payload, expected_status, expected_error
):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    response_update = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=headers
    )
    assert response_update.status_code == expected_status

    if expected_status == 200:
        updated_user = response_update.json()
        for field, value in update_payload.items():
            if value is not None:
                assert updated_user[field] == value
        response_get = await client.get(f"/users/{user_id}")
        assert response_get.status_code == 200
        user_from_db = response_get.json()
        for field, value in update_payload.items():
            if value is not None:
                assert user_from_db[field] == value

    elif expected_status == 422:
        error_detail = response_update.json()["detail"]
        if isinstance(error_detail, list):
            error_messages = [error.get("msg", "") for error in error_detail]
            assert any(expected_error in msg for msg in error_messages)
        else:
            assert expected_error in error_detail

    elif expected_status == 400:
        error_detail = response_update.json()["detail"]
        assert expected_error in error_detail


@pytest.mark.asyncio
async def test_update_user_doesnt_exist(client, user_with_token):

    user_id = "00000000-0000-0000-0000-000000000000"
    headers = user_with_token["headers"]

    update_payload = {"name": "NewName"}
    response = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=headers
    )
    assert response.status_code == 404
    assert "doesn't exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_invalid_uuid_format(client, user_with_token):

    invalid_user_id = "invalid-uuid-format"
    headers = user_with_token["headers"]

    update_payload = {"name": "NewName"}
    response = await client.patch(
        f"/users/{invalid_user_id}", json=update_payload, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_bio_validation(client, user_with_token):

    user_data = user_with_token["user_data"]
    user_id = user_data["user_id"]
    headers = user_with_token["headers"]

    long_bio = "a" * 5001
    update_payload = {"bio": long_bio}

    response = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=headers
    )
    assert response.status_code == 422

    detail = response.json()["detail"]
    if isinstance(detail, list):
        error_messages = [e.get("msg", "") for e in detail]
    else:
        error_messages = [detail]
    assert any("Bio must not exceed 5000 characters" in msg for msg in error_messages)

    valid_bio = "a" * 5000
    update_payload = {"bio": valid_bio}

    response = await client.patch(
        f"/users/{user_id}", json=update_payload, headers=headers
    )
    assert response.status_code == 200
