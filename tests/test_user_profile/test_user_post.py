import pytest

@pytest.mark.asyncio
async def test_create_user(client, data_user):
    response = await client.post("/users/", json=data_user)
    assert response.status_code == 201
    body = response.json()
    assert "user_id" in body
    body.pop("user_id")
    assert body == data_user

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, data_user):
    # Создаем первого пользователя
    response_first = await client.post("/users/", json=data_user)
    assert response_first.status_code == 201

    # Пытаемся создать такого жще пользователя (Уникальным быть должен только email)
    response_second = await client.post("/users/", json=data_user)
    assert response_second.status_code == 400
    assert "already exists" in response_second.json()["detail"]

@pytest.mark.parametrize(
    "payload,expected_status",
    [
        # Пустой payload
        ({}, 422),

        # Отсутствует обязательное поле email
        (
            {
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле name
        (
            {
                "email": "test1@example.com",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле surname
        (
            {
                "email": "test2@example.com",
                "name": "John",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле date_of_birth
        (
            {
                "email": "test3@example.com",
                "name": "John",
                "surname": "Doe",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле gender
        (
            {
                "email": "test4@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле country
        (
            {
                "email": "test5@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "city": "Moscow",
            },
            422,
        ),
        # Отсутствует обязательное поле city
        (
            {
                "email": "test6@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
            },
            422,
        ),
        # Отсутствует необязательное поле bio (должно пройти)
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
            201,
        ),
        # Несколько отсутствующих обязательных полей
        (
            {
                "email": "test8@example.com",
                "name": "John",
                # Отсутствуют: surname, date_of_birth, gender, country, city
            },
            422,
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_user_without_some_fields(client, payload, expected_status):
    response = await client.post("/users/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "payload,expected_status,expected_error",
    [
        # Превышение длины полей
        (
            {
                "email": "a" * 100 + "@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "value is not a valid email address",
        ),
        (
            {
                "email": "test@example.com",
                "name": "a" * 51,
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "a" * 51,
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "a" * 51,
                "city": "Moscow",
            },
            422,
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "a" * 51,
            },
            422,
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
                "bio": "a" * 5001,
            },
            422,
            "Bio must not exceed 5000 characters",
        ),
        # Валидация gender
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "x",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Gender must be m or f",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "mm",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "String should have at most 1 character",
        ),
        # Валидация даты рождения
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "2030-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Date of birth cannot be in the future",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "2010-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "User must be at least 18 years old",
        ),
        # None значения
        (
            {
                "email": None,
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": None,
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": None,
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": None,
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid date",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": None,
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        # Неправильные типы данных
        (
            {
                "email": 123,
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": 123,
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": 123,
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Datetimes provided to dates should have zero time",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": 123,
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        # Boolean значения
        (
            {
                "email": True,
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": False,
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        # Массивы и объекты
        (
            {
                "email": ["test@example.com"],
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": "test@example.com",
                "name": ["John"],
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        (
            {
                "email": {"email": "test@example.com"},
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid string",
        ),
        # Пустые строки
        (
            {
                "email": "test@example.com",
                "name": "",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "String should have at least 1 character",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "String should have at least 1 character",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "",
                "city": "Moscow",
            },
            422,
            "String should have at least 1 character",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "",
            },
            422,
            "String should have at least 1 character",
        ),
        # Неправильные форматы
        (
            {
                "email": "invalid-email",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "1990-01-01",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "value is not a valid email address",
        ),
        (
            {
                "email": "test@example.com",
                "name": "John",
                "surname": "Doe",
                "date_of_birth": "invalid-date",
                "gender": "m",
                "country": "Russia",
                "city": "Moscow",
            },
            422,
            "Input should be a valid date",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_user_with_field_validation_errors(
    client, payload, expected_status, expected_error
):
    response = await client.post("/users/", json=payload)
    assert response.status_code == expected_status

    if expected_status == 422:
        error_detail = response.json()["detail"]
        if isinstance(error_detail, list):
            error_messages = [error.get("msg", "") for error in error_detail]
            assert any(expected_error in msg for msg in error_messages)
        else:
            assert expected_error in error_detail
