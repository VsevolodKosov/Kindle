import pytest


@pytest.mark.asyncio
async def test_create_language_success(client):
    response = await client.post("/users/languages/", json={"name": "English"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "English"
    assert "id" in data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        ({"name": ""}, 422),
        ({"name": "a" * 51}, 422),
        ({}, 422),
        ({"name": None}, 422),
        ({"name": 123}, 422),
        ({"foo": "bar"}, 422),
        (None, 422),
    ],
)
async def test_create_language_invalid_payload(client, payload, expected_status):
    if payload is None:
        response = await client.post("/users/languages/", data=None)
    else:
        response = await client.post("/users/languages/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_create_language_duplicate_name(client):
    payload = {"name": "Spanish"}
    response1 = await client.post("/users/languages/", json=payload)
    assert response1.status_code == 200
    response2 = await client.post("/users/languages/", json=payload)
    assert response2.status_code in (400, 409)


@pytest.mark.asyncio
async def test_get_language_success(client, create_language):
    lang = await create_language({"name": "German"})
    response = await client.get(f"/users/languages/{lang['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lang["id"]
    assert data["name"] == "German"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lang_id, expected_status",
    [
        (99999, 404),
        ("abc", 422),
        ("", 200),
        (None, 404),
        (-1, 404),
        (0, 404),
    ],
)
async def test_get_language_not_found_or_invalid(client, lang_id, expected_status):
    response = await client.get(f"/users/languages/{lang_id}")
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_update_language_success(client, create_language):
    lang = await create_language({"name": "French"})
    response = await client.patch(
        f"/users/languages/{lang['id']}",
        json={"name": "Français"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Français"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status",
    [
        ({"name": ""}, 422),
        ({"name": "a" * 51}, 422),
        ({}, 422),
        ({"name": None}, 422),
        ({"name": 123}, 422),
        ({"foo": "bar"}, 422),
        (None, 422),
    ],
)
async def test_update_language_invalid_payload(
    client, create_language, update_data, expected_status
):
    lang = await create_language({"name": "TestLang"})
    if update_data is None:
        response = await client.patch(
            f"/users/languages/{lang['id']}",
            data=None,
        )
    else:
        response = await client.patch(
            f"/users/languages/{lang['id']}",
            json=update_data,
        )
    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lang_id, expected_status",
    [
        (99999, 404),
        ("abc", 422),
        ("", 422),
        (None, 404),
        (-1, 404),
        (0, 404),
    ],
)
async def test_update_language_not_found_or_invalid_id(
    client, lang_id, expected_status
):
    response = await client.patch(
        f"/users/languages/{lang_id}",
        json={"name": "NewName"},
    )
    assert response.status_code == expected_status



@pytest.mark.asyncio
async def test_update_language_duplicate_name(client, create_language):
    await create_language({"name": "Lang1"})
    lang2 = await create_language({"name": "Lang2"})
    response = await client.patch(
        f"/users/languages/{lang2['id']}",
        json={"name": "Lang1"},
    )
    assert response.status_code in (400, 409)


@pytest.mark.asyncio
async def test_delete_language_success(client, create_language):
    lang = await create_language({"name": "ToDelete"})
    response = await client.delete(f"/users/languages/{lang['id']}")
    assert response.status_code == 200
    response2 = await client.get(f"/users/languages/{lang['id']}")
    assert response2.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lang_id, expected_status",
    [
        (99999, 404),
        ("abc", 422),
        ("", 422),
        (None, 404),
        (-1, 404),
        (0, 404),
    ],
)
async def test_delete_language_not_found_or_invalid(client, lang_id, expected_status):
    response = await client.delete(f"/users/languages/{lang_id}")
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_delete_language_twice(client, create_language):
    lang = await create_language({"name": "ToDeleteTwice"})
    response1 = await client.delete(f"/users/languages/{lang['id']}")
    assert response1.status_code == 200
    response2 = await client.delete(f"/users/languages/{lang['id']}")
    assert response2.status_code in (404, 410)


@pytest.mark.asyncio
async def test_list_languages_empty(client):
    response = await client.get("/users/languages/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_languages_single(client, create_language):
    await create_language({"name": "Solo"})
    response = await client.get("/users/languages/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Solo"


@pytest.mark.asyncio
async def test_list_languages_multiple(client, create_language):
    await create_language({"name": "LangA"})
    await create_language({"name": "LangB"})
    response = await client.get("/users/languages/")
    assert response.status_code == 200
    data = response.json()
    names = [lang["name"] for lang in data]
    assert "LangA" in names and "LangB" in names
    assert len(data) >= 2
