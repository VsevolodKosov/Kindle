from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def data_social_link():
    return {
        "user_id": str(uuid4()),
        "title": "Instagram",
        "link": "https://instagram.com/username"
    }


@pytest.fixture
def data_user():
    return {
        "username": "Ivan",
        "email": "Ivan_Ivanov@mail.com",
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow"
    }


class TestSocialMediaLinks:
    @pytest.mark.asyncio
    async def test_create_social_link_success(
        self,
        client: AsyncClient,
        data_user,
        data_social_link,
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]

        response = await client.post("/users/social-links", json=data_social_link)
        assert response.status_code == 200

        link_data = response.json()
        assert link_data["user_id"] == user_data["id"]
        assert link_data["title"] == data_social_link["title"]
        assert link_data["link"] == data_social_link["link"]
        assert "id" in link_data

    @pytest.mark.asyncio
    async def test_create_social_link_invalid_data(
        self,
        client: AsyncClient,
        data_user,
        data_social_link
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]

        invalid_cases = [
            {},
            {"user_id": user_data["id"]},
            {"title": "Instagram"},
            {"link": "https://instagram.com/username"},
            {**data_social_link, "title": ""},
            {**data_social_link, "link": ""},
            {**data_social_link, "title": "a" * 101},
            {**data_social_link, "link": "a" * 256},
            {**data_social_link, "title": 12345},
            {**data_social_link, "link": ["url"]},
            {**data_social_link, "user_id": "not-a-uuid"},
            {**data_social_link, "user_id": str(uuid4())},
        ]

        for invalid_data in invalid_cases:
            response = await client.post(
                "/users/social-links",
                json=invalid_data
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_read_social_link_success(
        self,
        client: AsyncClient,
        data_user,
        data_social_link
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/social-links",
            json=data_social_link
        )
        assert create_response.status_code == 200
        link_data = create_response.json()

        response = await client.get(
            f"/users/social-links/{link_data['id']}"
        )
        assert response.status_code == 200

        read_data = response.json()
        assert read_data["id"] == link_data["id"]
        assert read_data["user_id"] == user_data["id"]
        assert read_data["title"] == data_social_link["title"]
        assert read_data["link"] == data_social_link["link"]

    @pytest.mark.asyncio
    async def test_read_social_link_not_found(self, client: AsyncClient):
        response = await client.get("/users/social-links/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_social_link_success(
        self,
        client: AsyncClient,
        data_user,
        data_social_link
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/social-links",
            json=data_social_link
        )
        assert create_response.status_code == 200
        link_data = create_response.json()

        update_data = {
            "title": "Updated Instagram",
            "link": "https://instagram.com/updated_username"
        }
        response = await client.patch(
            f"/users/social-links/{link_data['id']}",
            json=update_data
        )
        assert response.status_code == 200

        updated_data = response.json()
        assert updated_data["id"] == link_data["id"]
        assert updated_data["user_id"] == user_data["id"]
        assert updated_data["title"] == update_data["title"]
        assert updated_data["link"] == update_data["link"]

    @pytest.mark.asyncio
    async def test_update_social_link_invalid_data(
        self,
        client: AsyncClient,
        data_user,
        data_social_link
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/social-links",
            json=data_social_link
        )
        assert create_response.status_code == 200
        link_data = create_response.json()

        invalid_cases = [
            {"title": ""},
            {"link": ""},
            {"title": "a" * 101},
            {"link": "a" * 256},
            {"title": 12345},
            {"link": ["url"]},
        ]

        for invalid_data in invalid_cases:
            response = await client.patch(
                f"/users/social-links/{link_data['id']}",
                json=invalid_data
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_social_link_not_found(self, client: AsyncClient):
        update_data = {"title": "Updated Title"}
        response = await client.patch(
            "/users/social-links/99999",
            json=update_data
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_social_link_success(
        self,
        client: AsyncClient,
        data_user,
        data_social_link
    ):
        user_response = await client.post("/users/", json=data_user)
        assert user_response.status_code == 200
        user_data = user_response.json()

        data_social_link["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/social-links",
            json=data_social_link
        )
        assert create_response.status_code == 200
        link_data = create_response.json()

        response = await client.delete(
            f"/users/social-links/{link_data['id']}"
        )
        assert response.status_code == 200

        deleted_data = response.json()
        assert deleted_data["id"] == link_data["id"]
        assert deleted_data["user_id"] == user_data["id"]
        assert deleted_data["title"] == data_social_link["title"]
        assert deleted_data["link"] == data_social_link["link"]

        get_response = await client.get(
            f"/users/social-links/{link_data['id']}"
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_social_link_not_found(self, client: AsyncClient):
        response = await client.delete("/users/social-links/99999")
        assert response.status_code == 404
