import asyncio
import uuid
from typing import Any, AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.auth.utils import create_access_token
from src.database import get_async_db_session
from src.main import app
from tests.config import TEST_DATABASE_URL

CLEAN_TABLES = ["users", "user_photo", "user_social_media_links", "refresh_tokens"]


def clear_cookies(client: AsyncClient) -> None:
    client.cookies.clear()


@pytest.fixture
def clean_client(client: AsyncClient) -> AsyncClient:
    clear_cookies(client)
    return client


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_async_session():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_test_db_tables(test_db_async_session: AsyncSession):
    async with test_db_async_session.begin():
        for table in CLEAN_TABLES:
            await test_db_async_session.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))


async def get_test_db_async_session() -> AsyncGenerator[AsyncSession, None]:
    test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    test_async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    session = test_async_session()
    try:
        yield session
    finally:
        await session.close()
        await test_engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_db_session] = get_test_db_async_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as async_client:
        yield async_client


@pytest.fixture
def data_user() -> Dict[str, Any]:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"Ivan_{unique_id}@mail.com",
        "name": "Ivan",
        "surname": "Ivanov",
        "date_of_birth": "1990-05-15",
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
        "password": "TestPassword123!",
    }


@pytest.fixture
def data_user_photo() -> Dict[str, str]:
    return {"url": "https://example.com/photo.jpg"}


@pytest.fixture
def data_user_social_link() -> Dict[str, str]:
    return {"link": "https://t.me/example", "name": "Telegram"}


@pytest.fixture
def data_moderator() -> Dict[str, Any]:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"moderator_{unique_id}@mail.com",
        "name": "Moderator",
        "surname": "User",
        "date_of_birth": "1985-01-01",
        "bio": "A moderator user",
        "gender": "f",
        "country": "Russia",
        "city": "Moscow",
        "password": "ModeratorPass123!",
    }


@pytest.fixture
def data_admin() -> Dict[str, Any]:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"admin_{unique_id}@mail.com",
        "name": "Admin",
        "surname": "User",
        "date_of_birth": "1980-01-01",
        "bio": "An admin user",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
        "password": "AdminPass123!",
    }


@pytest.fixture
def data_user_with_password() -> Dict[str, Any]:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"Ivan_{unique_id}@mail.com",
        "name": "Ivan",
        "surname": "Ivanov",
        "date_of_birth": "1990-05-15",
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
        "password": "TestPassword123!",
    }


@pytest_asyncio.fixture
async def user_with_token(client, data_user_with_password):
    """Создает пользователя и возвращает его данные с токеном"""
    response = await client.post("/auth/register", json=data_user_with_password)
    assert response.status_code == 201

    login_data = {
        "email": data_user_with_password["email"],
        "password": data_user_with_password["password"],
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    clear_cookies(client)

    from jose import jwt

    from src.config import SECRET_KEY

    token_payload = jwt.decode(
        token_data["access_token"], SECRET_KEY, algorithms=["HS256"]
    )
    user_id = token_payload["sub"]

    return {
        "user_data": {"user_id": user_id, **data_user_with_password},
        "access_token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
    }


@pytest_asyncio.fixture
async def moderator_with_token(client, data_moderator):
    """Создает модератора и возвращает его данные с токеном"""
    response = await client.post("/auth/register", json=data_moderator)
    assert response.status_code == 201
    user_data = response.json()

    login_data = {
        "email": data_moderator["email"],
        "password": data_moderator["password"],
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    clear_cookies(client)

    return {
        "user": user_data,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
    }


@pytest_asyncio.fixture
async def admin_with_token(client, data_admin):
    """Создает админа и возвращает его данные с токеном"""
    response = await client.post("/auth/register", json=data_admin)
    assert response.status_code == 201
    user_data = response.json()

    login_data = {"email": data_admin["email"], "password": data_admin["password"]}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()

    from jose import jwt

    from src.config import SECRET_KEY

    token_payload = jwt.decode(
        token_data["access_token"], SECRET_KEY, algorithms=["HS256"]
    )
    user_id = token_payload["sub"]

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = await client.post(f"/admin/users/{user_id}/promote", headers=headers)

    admin_token = create_access_token(payload={"sub": user_id, "role": "admin"})
    clear_cookies(client)

    return {
        "user": user_data,
        "token": admin_token,
        "headers": {"Authorization": f"Bearer {admin_token}"},
    }


@pytest_asyncio.fixture
async def two_users_with_tokens(client, data_user_with_password):
    """Создает двух пользователей и возвращает их данные с токенами"""
    user1_data = {**data_user_with_password}
    user1_data["email"] = f"user1_{str(uuid.uuid4())[:8]}@mail.com"

    response1 = await client.post("/auth/register", json=user1_data)
    assert response1.status_code == 201

    login1 = await client.post(
        "/auth/login",
        json={"email": user1_data["email"], "password": user1_data["password"]},
    )
    assert login1.status_code == 200
    token_data1 = login1.json()
    token1 = token_data1["access_token"]
    clear_cookies(client)

    from jose import jwt

    from src.config import SECRET_KEY

    token_payload1 = jwt.decode(token1, SECRET_KEY, algorithms=["HS256"])
    user1_id = token_payload1["sub"]

    user2_data = {**data_user_with_password}
    user2_data["email"] = f"user2_{str(uuid.uuid4())[:8]}@mail.com"

    response2 = await client.post("/auth/register", json=user2_data)
    assert response2.status_code == 201

    login2 = await client.post(
        "/auth/login",
        json={"email": user2_data["email"], "password": user2_data["password"]},
    )
    assert login2.status_code == 200
    token_data2 = login2.json()
    token2 = token_data2["access_token"]
    clear_cookies(client)

    token_payload2 = jwt.decode(token2, SECRET_KEY, algorithms=["HS256"])
    user2_id = token_payload2["sub"]

    return {
        "user1": {
            "user_data": {"user_id": user1_id, **user1_data},
            "access_token": token1,
            "headers": {"Authorization": f"Bearer {token1}"} if token1 else {},
        },
        "user2": {
            "user_data": {"user_id": user2_id, **user2_data},
            "access_token": token2,
            "headers": {"Authorization": f"Bearer {token2}"} if token2 else {},
        },
    }
