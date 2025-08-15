import pytest

@pytest.mark.asyncio
async def test_update_user_duplicate_email(client, data_user):

    # Создаем первого пользователя
    response_first = await client.post("/users/", json=data_user)
    assert response_first.status_code == 201
    first_user_id = response_first.json()["user_id"]

    # Создаем второго пользователя с другим email
    second_user_data = {**data_user, "email": "second@example.com"}
    response_second = await client.post("/users/", json=second_user_data)
    assert response_second.status_code == 201
    second_user_id = response_second.json()["user_id"]

    # Пытаемся обновить email второго пользователя на email первого
    update_payload = {"email": data_user["email"]}
    response_update = await client.patch(f"/users/{second_user_id}", json=update_payload)

    # Должна вернуться ошибка 400 с сообщением о дублирующем email
    assert response_update.status_code == 400
    error_detail = response_update.json()["detail"]
    assert "already exists" in error_detail

    # Проверяем что email второго пользователя не изменился
    response_get = await client.get(f"/users/{second_user_id}")
    assert response_get.status_code == 200
    user_data = response_get.json()
    assert user_data["email"] == "second@example.com"

    # Проверяем что первый пользователь не пострадал
    response_get_first = await client.get(f"/users/{first_user_id}")
    assert response_get_first.status_code == 200
    first_user_data = response_get_first.json()
    assert first_user_data["email"] == data_user["email"]


@pytest.mark.parametrize(
    "update_payload,expected_status,expected_error",
    [
        # Успешные обновления отдельных полей
        ({"email": "newemail@example.com"}, 200, None),
        ({"name": "NewName"}, 200, None),
        ({"surname": "NewSurname"}, 200, None),
        ({"date_of_birth": "1985-06-20"}, 200, None),
        ({"bio": "Новая биография пользователя"}, 200, None),
        ({"gender": "f"}, 200, None),
        ({"country": "Russia"}, 200, None),
        ({"city": "Moscow"}, 200, None),

        # Обновление нескольких полей одновременно
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

        ({"bio": None}, 404, None),

        # Обновление bio с пустой строки на значение
        ({"bio": "Восстановленная биография"}, 200, None),

        # Валидационные ошибки  email
        ({"email": "invalid-email"}, 422, "value is not a valid email address"),
        (
            {"email": "a" * 100 + "@example.com"},
            422,
            "value is not a valid email address",
        ),
        ({"email": ""}, 422, "value is not a valid email address"),

        # Валидационные ошибки name
        ({"name": ""}, 422, "String should have at least 1 character"),
        ({"name": "   "}, 422, "String should have at least 1 character"),
        ({"name": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"name": None}, 404, None),

        # Валидационные ошибки  surname
        ({"surname": ""}, 422, "String should have at least 1 character"),
        ({"surname": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"surname": None}, 404, None),

        ({"date_of_birth": "invalid-date"}, 422, "Input should be a valid date"),
        ({"date_of_birth": None}, 404, None),
        ({"date_of_birth": 123}, 422, "zero time"),

        # Валидационные ошибки  gender
        ({"gender": "x"}, 422, "Gender must be 'm' or 'f'"),
        ({"gender": "mm"}, 422, "String should have at most 1 character"),
        ({"gender": "M"}, 422, "Gender must be 'm' or 'f'"),
        ({"gender": "male"}, 422, "String should have at most 1 character"),
        ({"gender": ""}, 422, "String should have at least 1 character"),
        ({"gender": None}, 404, None),

        # Валидационные ошибки country
        ({"country": ""}, 422, "String should have at least 1 character"),
        ({"country": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"country": None}, 404, None),

        # Валидационные ошибки city
        ({"city": ""}, 422, "String should have at least 1 character"),
        ({"city": "a" * 51}, 422, "String should have at most 50 characters"),
        ({"city": None}, 404, None),


        # Неправильные типы данных
        ({"email": 123}, 422, "Input should be a valid string"),
        ({"name": 123}, 422, "Input should be a valid string"),
        ({"surname": True}, 422, "Input should be a valid string"),
        ({"gender": 123}, 422, "Input should be a valid string"),
        ({"country": ["Russia"]}, 422, "Input should be a valid string"),
        ({"city": {"city": "Moscow"}}, 422, "Input should be a valid string"),

        # Пустой payload
        ({}, 400, "No data provided for update"),

        # Граничные значения
        ({"name": "a" * 50}, 200, None),
        ({"bio": "a" * 5000}, 200, None),
        ({"date_of_birth": "2006-08-15"}, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_update_user_comprehensive(
    client, data_user, update_payload, expected_status, expected_error
):
    response_post = await client.post("/users/", json=data_user)
    assert response_post.status_code == 201
    user_id = response_post.json()["user_id"]

    response_update = await client.patch(f"/users/{user_id}", json=update_payload)
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
