from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def data_user():
    return {
        "username": "Ivan",
        "email": "Ivan_Ivanov@mail.com",
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
    }


@pytest.fixture
def data_language():
    return {"name": "English"}


@pytest.fixture
def data_user_language():
    return {
        "user_id": str(uuid4()),
        "language_id": 1,
    }


class TestUserLanguages:
    @pytest.mark.asyncio
    async def test_add_language_to_user_success(
        self, client: AsyncClient, data_user, data_language
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        user_language_data = {
            "user_id": user_data["id"],
            "language_id": language_data["id"],
        }

        response = await client.post(
            f"/users/{user_data['id']}/languages",
            json=user_language_data,
        )
        assert response.status_code == 200

        user_language_response = response.json()
        assert user_language_response["user_id"] == user_data["id"]
        assert user_language_response["language_id"] == language_data["id"]

    @pytest.mark.asyncio
    async def test_add_language_to_user_invalid_data(
        self, client: AsyncClient, data_user, data_language
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        invalid_cases = [
            {},
            {"user_id": user_data["id"]},
            {"language_id": language_data["id"]},
            {"user_id": 12345, "language_id": language_data["id"]},
            {
                "user_id": user_data["id"],
                "language_id": "not-a-number",
            },
            {
                "user_id": "not-a-uuid",
                "language_id": language_data["id"],
            },
            {
                "user_id": str(uuid4()),
                "language_id": language_data["id"],
            },
            {"user_id": user_data["id"], "language_id": 99999},
        ]

        for invalid_data in invalid_cases:
            response = await client.post(
                f"/users/{user_data['id']}/languages",
                json=invalid_data,
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_add_duplicate_language_to_user(
        self, client: AsyncClient, data_user, data_language
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        user_language_data = {
            "user_id": user_data["id"],
            "language_id": language_data["id"],
        }

        response = await client.post(
            f"/users/{user_data['id']}/languages",
            json=user_language_data,
        )
        assert response.status_code == 200

        response = await client.post(
            f"/users/{user_data['id']}/languages",
            json=user_language_data,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_read_user_languages_success(
        self, client: AsyncClient, data_user
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        languages = []
        for lang_name in ["English", "Russian", "Spanish"]:
            language_response = await client.post(
                "/users/languages/", json={"name": lang_name}
            )
            assert language_response.status_code == 200
            languages.append(language_response.json())

        for language in languages:
            user_language_data = {
                "user_id": user_data["id"],
                "language_id": language["id"],
            }
            response = await client.post(
                f"/users/{user_data['id']}/languages",
                json=user_language_data,
            )
            assert response.status_code == 200

        response = await client.get(
            f"/users/{user_data['id']}/languages"
        )
        assert response.status_code == 200

        user_languages = response.json()
        assert len(user_languages) == 3

        language_ids = [lang["language_id"] for lang in user_languages]
        expected_ids = [lang["id"] for lang in languages]
        assert set(language_ids) == set(expected_ids)

        for user_lang in user_languages:
            assert user_lang["user_id"] == user_data["id"]

    @pytest.mark.asyncio
    async def test_read_user_languages_empty(
        self, client: AsyncClient, data_user
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        response = await client.get(
            f"/users/{user_data['id']}/languages"
        )
        assert response.status_code == 200

        user_languages = response.json()
        assert user_languages == []

    @pytest.mark.asyncio
    async def test_read_user_languages_user_not_found(
        self, client: AsyncClient
    ):
        fake_user_id = str(uuid4())
        response = await client.get(f"/{fake_user_id}/languages")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_language_from_user_success(
        self, client: AsyncClient, data_user, data_language
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        user_language_data = {
            "user_id": user_data["id"],
            "language_id": language_data["id"],
        }

        response = await client.post(
            f"/users/{user_data['id']}/languages",
            json=user_language_data,
        )
        assert response.status_code == 200

        response = await client.delete(
            f"/users/{user_data['id']}/languages/{language_data['id']}"
        )
        assert response.status_code == 204

        languages_response = await client.get(
            f"/users/{user_data['id']}/languages"
        )
        assert languages_response.status_code == 200
        assert languages_response.json() == []

    @pytest.mark.asyncio
    async def test_remove_language_from_user_not_found(
        self, client: AsyncClient, data_user, data_language
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        response = await client.delete(
            f"/users/{user_data['id']}/languages/{language_data['id']}"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_language_from_user_user_not_found(
        self, client: AsyncClient, data_language
    ):
        language_response = await client.post(
            "/users/languages/", json=data_language
        )
        assert language_response.status_code == 200
        language_data = language_response.json()

        fake_user_id = str(uuid4())
        response = await client.delete(
            f"/users/{fake_user_id}/languages/{language_data['id']}"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_language_from_user_language_not_found(
        self, client: AsyncClient, data_user
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        response = await client.delete(
            f"/users/{user_data['id']}/languages/99999"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_multiple_languages_operations(
        self, client: AsyncClient, data_user
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        languages = []
        for lang_name in ["English", "Russian", "Spanish", "French"]:
            language_response = await client.post(
                "/users/languages/", json={"name": lang_name}
            )
            assert language_response.status_code == 200
            languages.append(language_response.json())

        for language in languages:
            user_language_data = {
                "user_id": user_data["id"],
                "language_id": language["id"],
            }
            response = await client.post(
                f"/users/{user_data['id']}/languages",
                json=user_language_data,
            )
            assert response.status_code == 200

        response = await client.get(
            f"/users/{user_data['id']}/languages"
        )
        assert response.status_code == 200
        user_languages = response.json()
        assert len(user_languages) == 4

        language_to_remove = languages[1]
        response = await client.delete(
            f"/users/{user_data['id']}/languages/"
            f"{language_to_remove['id']}"
        )
        assert response.status_code == 204

        response = await client.get(
            f"/users/{user_data['id']}/languages"
        )
        assert response.status_code == 200
        user_languages = response.json()
        assert len(user_languages) == 3

        language_ids = [lang["language_id"] for lang in user_languages]
        assert language_to_remove["id"] not in language_ids
