import asyncio
from copy import deepcopy
from typing import AsyncGenerator

import asyncpg
import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import get_db_async_session
from src.main import app
from tests.config import TEST_DATABASE_URL

CLEAN_TABLES = [
    "user_photos",
    "user_social_media_links",
    "user_languages",
    "languages",
    "users",
]


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_session_test():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def clean_tables_db(async_session_test):
    async with async_session_test() as db_session:
        async with db_session.begin():
            for table in CLEAN_TABLES:
                await db_session.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))


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


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db_async_session] = get_test_db_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool("".join(TEST_DATABASE_URL.split("+asyncpg")))
    yield pool
    await pool.close()


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
async def create_user(asyncpg_pool, data_user):
    async def _create_user(data=None):
        data = deepcopy(data or data_user)
        async with asyncpg_pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO users(username, email, bio, gender, country, city)
                VALUES($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                data["username"],
                data["email"],
                data["bio"],
                data["gender"],
                data["country"],
                data["city"],
            )
            data["id"] = record["id"]
        return data

    return _create_user


@pytest.fixture
async def get_user(asyncpg_pool):
    async def _get_user(id):
        async with asyncpg_pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE id = $1", id)

    return _get_user


@pytest.fixture
async def update_user(asyncpg_pool):
    async def _update_user(
        id,
        username=None,
        email=None,
        bio=None,
        gender=None,
        country=None,
        city=None,
    ):
        set_clauses = []
        values = []
        idx = 1

        if username is not None:
            set_clauses.append(f"username = ${idx}")
            values.append(username)
            idx += 1
        if email is not None:
            set_clauses.append(f"email = ${idx}")
            values.append(email)
            idx += 1
        if bio is not None:
            set_clauses.append(f"bio = ${idx}")
            values.append(bio)
            idx += 1
        if gender is not None:
            set_clauses.append(f"gender = ${idx}")
            values.append(gender)
            idx += 1
        if country is not None:
            set_clauses.append(f"country = ${idx}")
            values.append(country)
            idx += 1
        if city is not None:
            set_clauses.append(f"city = ${idx}")
            values.append(city)
            idx += 1

        if not set_clauses:
            return

        set_clause = ", ".join(set_clauses)
        values.append(id)
        query = f"UPDATE users SET {set_clause} WHERE id = ${idx}"

        async with asyncpg_pool.acquire() as conn:
            await conn.execute(query, *values)

    return _update_user


@pytest.fixture
async def delete_user(asyncpg_pool):
    async def _delete_user(id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute("DELETE FROM users WHERE id = $1", id)

    return _delete_user


@pytest.fixture
def data_language():
    return {"name": "English"}


@pytest.fixture
async def create_language(asyncpg_pool, data_language):
    async def _create_language(data=None):
        data = deepcopy(data or data_language)
        async with asyncpg_pool.acquire() as conn:
            record = await conn.fetchrow(
                "INSERT INTO languages(name) VALUES($1) RETURNING id", data["name"]
            )
            data["id"] = record["id"]
        return data

    return _create_language


@pytest.fixture
async def get_language(asyncpg_pool):
    async def _get_language(id):
        async with asyncpg_pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM languages WHERE id = $1", id)

    return _get_language


@pytest.fixture
async def update_language(asyncpg_pool):
    async def _update_language(id, **kwargs):
        set_clauses = []
        values = []
        idx = 1
        for field, val in kwargs.items():
            set_clauses.append(f"{field} = ${idx}")
            values.append(val)
            idx += 1
        if not set_clauses:
            return
        set_clause = ", ".join(set_clauses)
        values.append(id)
        query = f"UPDATE languages SET {set_clause} WHERE id = ${idx}"
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(query, *values)

    return _update_language


@pytest.fixture
async def delete_language(asyncpg_pool):
    async def _delete_language(id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute("DELETE FROM languages WHERE id = $1", id)

    return _delete_language


@pytest.fixture
async def create_user_language(asyncpg_pool):
    async def _create_user_language(user_id, language_id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO user_languages(user_id, language_id) VALUES($1, $2)",
                user_id,
                language_id,
            )

    return _create_user_language


@pytest.fixture
async def delete_user_language(asyncpg_pool):
    async def _delete_user_language(user_id, language_id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM user_languages WHERE user_id = $1 AND language_id = $2",
                user_id,
                language_id,
            )

    return _delete_user_language


@pytest.fixture
def data_user_social_media_link():
    return {
        "user_id": None,
        "title": "Facebook",
        "link": "https://facebook.com/ivan",
    }


@pytest.fixture
async def create_user_social_media_link(asyncpg_pool, data_user_social_media_link):
    async def _create_link(data=None):
        data = deepcopy(data or data_user_social_media_link)
        async with asyncpg_pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO user_social_media_links(user_id, title, link)
                VALUES($1, $2, $3)
                RETURNING id
                """,
                data["user_id"],
                data["title"],
                data["link"],
            )
            data["id"] = record["id"]
        return data

    return _create_link


@pytest.fixture
async def get_user_social_media_link(asyncpg_pool):
    async def _get_link(id):
        async with asyncpg_pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM user_social_media_links WHERE id = $1", id
            )

    return _get_link


@pytest.fixture
async def update_user_social_media_link(asyncpg_pool):
    async def _update_link(id, **kwargs):
        set_clauses = []
        values = []
        idx = 1
        for field, val in kwargs.items():
            set_clauses.append(f"{field} = ${idx}")
            values.append(val)
            idx += 1
        if not set_clauses:
            return
        set_clause = ", ".join(set_clauses)
        values.append(id)
        query = f"UPDATE user_social_media_links SET {set_clause} WHERE id = ${idx}"
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(query, *values)

    return _update_link


@pytest.fixture
async def delete_user_social_media_link(asyncpg_pool):
    async def _delete_link(id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM user_social_media_links WHERE id = $1", id
            )

    return _delete_link


@pytest.fixture
def data_user_photo():
    return {
        "user_id": None,
        "photo_link": "https://example.com/photo.jpg",
    }


@pytest.fixture
async def create_user_photo(asyncpg_pool, data_user_photo):
    async def _create_photo(data=None):
        data = deepcopy(data or data_user_photo)
        async with asyncpg_pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                INSERT INTO user_photos(user_id, photo_link)
                VALUES($1, $2)
                RETURNING id
                """,
                data["user_id"],
                data["photo_link"],
            )
            data["id"] = record["id"]
        return data

    return _create_photo


@pytest.fixture
async def get_user_photo(asyncpg_pool):
    async def _get_photo(id):
        async with asyncpg_pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM user_photos WHERE id = $1", id
            )

    return _get_photo


@pytest.fixture
async def update_user_photo(asyncpg_pool):
    async def _update_photo(id, **kwargs):
        set_clauses = []
        values = []
        idx = 1
        for field, val in kwargs.items():
            set_clauses.append(f"{field} = ${idx}")
            values.append(val)
            idx += 1
        if not set_clauses:
            return
        set_clause = ", ".join(set_clauses)
        values.append(id)
        query = f"UPDATE user_photos SET {set_clause} WHERE id = ${idx}"
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(query, *values)

    return _update_photo


@pytest.fixture
async def delete_user_photo(asyncpg_pool):
    async def _delete_photo(id):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute("DELETE FROM user_photos WHERE id = $1", id)

    return _delete_photo
