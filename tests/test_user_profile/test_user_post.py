import pytest


@pytest.mark.asyncio
async def test_register_user_success(client, data_user):

    response = await client.post("/auth/register", json=data_user)
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert "password" not in body
    assert body["access_token"]
    assert body["refresh_token"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client, data_user):

    response_first = await client.post("/auth/register", json=data_user)
    assert response_first.status_code == 201

    response_second = await client.post("/auth/register", json=data_user)
    assert response_second.status_code == 400
    assert "already exists" in response_second.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email_different_password(client, data_user):

    response_first = await client.post("/auth/register", json=data_user)
    assert response_first.status_code == 201

    duplicate_user = {**data_user}
    duplicate_user["password"] = "DifferentPassword123!"
    response_second = await client.post("/auth/register", json=duplicate_user)
    assert response_second.status_code == 400
    assert "already exists" in response_second.json()["detail"]


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({}, 422),
        (
            {
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test1@example.com",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test2@example.com",
                "name": "John",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test3@example.com",
                "name": "John",
                "surname": "Doe",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test4@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "country": "Russia",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test5@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "city": "Moscow",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test6@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "password": "TestPassword123!",
            },
            422,
        ),
        (
            {
                "email": "test7@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
    ],
)
@pytest.mark.asyncio
async def test_register_user_validation_errors(client, payload, expected_status):

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "field,invalid_value,expected_error",
    [
        ("email", "invalid-email", "value is not a valid email address"),
        ("email", "", "value is not a valid email address"),
        ("email", "a" * 100 + "@example.com", "value is not a valid email address"),
        ("name", "", "String should have at least 1 character"),
        ("name", "   ", "String should have at least 1 character"),
        ("name", "a" * 51, "String should have at most 50 characters"),
        ("surname", "", "String should have at least 1 character"),
        ("surname", "a" * 51, "String should have at most 50 characters"),
        ("date_of_birth", "invalid-date", "Input should be a valid date"),
        ("date_of_birth", "2026-01-01", "Date of birth cannot be in the future"),
        ("date_of_birth", "2010-01-01", "User must be at least 18 years old"),
        ("gender", "x", "Gender must be m or f"),
        ("gender", "mm", "String should have at most 1 character"),
        ("gender", "M", "Gender must be m or f"),
        ("gender", "male", "String should have at most 1 character"),
        ("gender", "", "String should have at least 1 character"),
        ("country", "", "String should have at least 1 character"),
        ("country", "   ", "String should have at least 1 character"),
        ("country", "a" * 51, "String should have at most 50 characters"),
        ("city", "", "String should have at least 1 character"),
        ("city", "   ", "String should have at least 1 character"),
        ("city", "a" * 51, "String should have at most 50 characters"),
        ("password", "short", "String should have at least 8 characters"),
        ("password", "", "String should have at least 8 characters"),
    ],
)
@pytest.mark.asyncio
async def test_register_user_field_validation(
    client, field, invalid_value, expected_error
):

    user_data = {
        "email": "test@example.com",
        "name": "John",
        "surname": "Doe",
        "date_of_birth": "1990-01-01",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
        "password": "TestPassword123!",
    }

    user_data[field] = invalid_value

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 422

    detail = response.json()["detail"]
    if isinstance(detail, list):
        error_messages = [e.get("msg", "") for e in detail]
    else:
        error_messages = [detail]

    assert any(expected_error in msg for msg in error_messages)


@pytest.mark.asyncio
async def test_register_user_bio_validation(client, data_user):

    long_bio_user = {**data_user}
    long_bio_user["bio"] = "a" * 5001

    response = await client.post("/auth/register", json=long_bio_user)
    assert response.status_code == 422
    detail = response.json()["detail"]
    if isinstance(detail, list):
        error_messages = [e.get("msg", "") for e in detail]
    else:
        error_messages = [detail]
    assert any("Bio must not exceed 5000 characters" in msg for msg in error_messages)

    valid_bio_user = {**data_user}
    valid_bio_user["email"] = "validbio@example.com"
    valid_bio_user["bio"] = "a" * 5000

    response = await client.post("/auth/register", json=valid_bio_user)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_user_successful_login_after_registration(client, data_user):

    response = await client.post("/auth/register", json=data_user)
    assert response.status_code == 201

    login_data = {"email": data_user["email"], "password": data_user["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    cookies = login_response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies


@pytest.mark.asyncio
async def test_register_user_password_hashing(client, data_user):

    response = await client.post("/auth/register", json=data_user)
    assert response.status_code == 201

    login_data = {"email": data_user["email"], "password": data_user["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    wrong_login_data = {"email": data_user["email"], "password": "WrongPassword123!"}
    wrong_login_response = await client.post("/auth/login", json=wrong_login_data)

    assert wrong_login_response.status_code == 400
    assert "Incorrect email or password" in wrong_login_response.json()["detail"]
