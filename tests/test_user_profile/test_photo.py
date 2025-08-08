from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def data_photo():
    return {
        "user_id": str(uuid4()),
        "url": "https://example.com/photo.jpg",
        "description": "My profile photo"
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


class TestPhotos:
    @pytest.mark.asyncio
    async def test_create_photo_success(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        response = await client.post(
            "/users/photos",
            json=data_photo,
        )
        assert response.status_code == 200
        photo_data = response.json()
        assert photo_data["user_id"] == user_data["id"]
        assert photo_data["url"] == data_photo["url"]
        assert photo_data["description"] == data_photo["description"]
        assert "id" in photo_data

    @pytest.mark.asyncio
    async def test_create_photo_without_description(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        photo_data = {
            "user_id": user_data["id"],
            "url": "https://example.com/photo.jpg",
        }
        response = await client.post(
            "/users/photos",
            json=photo_data,
        )
        assert response.status_code == 200
        photo_response = response.json()
        assert photo_response["user_id"] == user_data["id"]
        assert photo_response["url"] == photo_data["url"]
        assert photo_response["description"] is None

    @pytest.mark.asyncio
    async def test_create_photo_invalid_data(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        invalid_cases = [
            {},
            {"user_id": user_data["id"]},
            {"url": "https://example.com/photo.jpg"},
            {**data_photo, "url": ""},
            {**data_photo, "url": "a" * 256},
            {**data_photo, "description": "a" * 5001},
            {**data_photo, "url": 12345},
            {**data_photo, "description": ["text"]},
            {**data_photo, "user_id": "not-a-uuid"},
            {**data_photo, "user_id": str(uuid4())},
        ]
        for invalid_data in invalid_cases:
            response = await client.post(
                "/users/photos",
                json=invalid_data,
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_read_photo_success(self, client: AsyncClient, data_user, data_photo):

        user_response = await client.post(
            "/users/", json=data_user
        )
        assert user_response.status_code == 200
        user_data = user_response.json()


        data_photo["user_id"] = user_data["id"]
        create_response = await client.post("/users/photos", json=data_photo)
        assert create_response.status_code == 200
        photo_data = create_response.json()


        response = await client.get(
            f"/users/photos/{photo_data['id']}"
        )
        assert response.status_code == 200

        read_data = response.json()
        assert read_data["id"] == photo_data["id"]
        assert read_data["user_id"] == user_data["id"]
        assert read_data["url"] == data_photo["url"]
        assert read_data["description"] == data_photo["description"]

    @pytest.mark.asyncio
    async def test_read_photo_not_found(self, client: AsyncClient):

        response = await client.get("/users/photos/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_photo_success(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/photos",
            json=data_photo,
        )
        assert create_response.status_code == 200
        photo_data = create_response.json()
        update_data = {
            "url": "https://example.com/updated_photo.jpg",
            "description": "Updated photo description",
        }
        response = await client.patch(
            f"/users/photos/{photo_data['id']}",
            json=update_data,
        )
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["id"] == photo_data["id"]
        assert updated_data["user_id"] == user_data["id"]
        assert updated_data["url"] == update_data["url"]
        assert updated_data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_photo_partial(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/photos",
            json=data_photo,
        )
        assert create_response.status_code == 200
        photo_data = create_response.json()
        update_data = {"url": "https://example.com/new_photo.jpg"}
        response = await client.patch(
            f"/users/photos/{photo_data['id']}",
            json=update_data,
        )
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["url"] == update_data["url"]
        assert updated_data["description"] == data_photo["description"]
        update_data = {"description": "New description"}
        response = await client.patch(
            f"/users/photos/{photo_data['id']}",
            json=update_data,
        )
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["url"] == "https://example.com/new_photo.jpg"
        assert updated_data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_photo_invalid_data(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/photos",
            json=data_photo,
        )
        assert create_response.status_code == 200
        photo_data = create_response.json()
        invalid_cases = [
            {"url": ""},
            {"url": "a" * 256},
            {"description": "a" * 5001},
            {"url": 12345},
            {"description": ["text"]},
        ]
        for invalid_data in invalid_cases:
            response = await client.patch(
                f"/users/photos/{photo_data['id']}",
                json=invalid_data,
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_photo_not_found(self, client: AsyncClient):

        update_data = {"url": "https://example.com/new_photo.jpg"}
        response = await client.patch("/users/photos/99999", json=update_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_photo_success(
        self,
        client: AsyncClient,
        data_user,
        data_photo,
    ):
        user_response = await client.post(
            "/users/",
            json=data_user,
        )
        assert user_response.status_code == 200
        user_data = user_response.json()
        data_photo["user_id"] = user_data["id"]
        create_response = await client.post(
            "/users/photos",
            json=data_photo,
        )
        assert create_response.status_code == 200
        photo_data = create_response.json()
        response = await client.delete(
            f"/users/photos/{photo_data['id']}"
        )
        assert response.status_code == 200
        deleted_data = response.json()
        assert deleted_data["id"] == photo_data["id"]
        assert deleted_data["user_id"] == user_data["id"]
        assert deleted_data["url"] == data_photo["url"]
        assert deleted_data["description"] == data_photo["description"]
        get_response = await client.get(
            f"/users/photos/{photo_data['id']}"
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_photo_not_found(self, client: AsyncClient):

        response = await client.delete("/users/photos/99999")
        assert response.status_code == 404
