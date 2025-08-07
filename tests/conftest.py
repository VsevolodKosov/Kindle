import asyncio
from copy import deepcopy
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import get_db_async_session
from src.main import app
from src.user_profile.models import Language
from src.user_profile.models import User
from src.user_profile.models import UserLanguage
from src.user_profile.models import UserPhoto
from src.user_profile.models import UserSocialMediaLink
from tests.config import TEST_DATABASE_URL

CLEAN_TABLES = [
    "user_photos",
    "user_social_media_links",
    "user_languages",
    "languages",
    "users"
]

@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def async_session_test():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    yield async_session
    await engine.dispose()

@pytest.fixture(scope="function", autouse=True)
async def clean_tables_db(async_session_test):
    async with async_session_test() as db_session:
        async with db_session.begin():
            for table in CLEAN_TABLES:
                await db_session.execute(
                    text(f"TRUNCATE TABLE {table} CASCADE;")
                )

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
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as async_client:
        yield async_client

@pytest.fixture
def get_data_user():
    return {
        "username": "Ivan",
        "email": "Ivan_Ivanov@mail.com",
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
    }

@pytest.fixture
async def create_user(async_session_test, get_data_user):
    async def _create_user(data=None):
        data = deepcopy(data or get_data_user)
        async with async_session_test() as session:
            user = User(**data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            data["id"] = user.id
        return data
    return _create_user

@pytest.fixture
async def get_user(async_session_test):
    async def _get_user(id):
        async with async_session_test() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE id = :id"), {"id": id}
            )
            return result.fetchone()
    return _get_user

@pytest.fixture
async def update_user(async_session_test):
    async def _update_user(
        id,
        username=None,
        email=None,
        bio=None,
        gender=None,
        country=None,
        city=None,
    ):
        async with async_session_test() as session:
            update_data = {}
            if username is not None:
                update_data["username"] = username
            if email is not None:
                update_data["email"] = email
            if bio is not None:
                update_data["bio"] = bio
            if gender is not None:
                update_data["gender"] = gender
            if country is not None:
                update_data["country"] = country
            if city is not None:
                update_data["city"] = city

            if update_data:
                set_clause = ", ".join(
                    [f"{k} = :{k}" for k in update_data.keys()]
                )
                query = f"UPDATE users SET {set_clause} WHERE id = :id"
                update_data["id"] = id
                await session.execute(text(query), update_data)
                await session.commit()

    return _update_user

@pytest.fixture
async def delete_user(async_session_test):
    async def _delete_user(id):
        async with async_session_test() as session:
            await session.execute(
                text("DELETE FROM users WHERE id = :id"), {"id": id}
            )
            await session.commit()
    return _delete_user

@pytest.fixture
def get_data_language():
    return {"name": "English"}

@pytest.fixture
async def create_language(async_session_test, get_data_language):
    async def _create_language(data=None):
        data = deepcopy(data or get_data_language)
        async with async_session_test() as session:
            language = Language(**data)
            session.add(language)
            await session.commit()
            await session.refresh(language)
            data["id"] = language.id
        return data
    return _create_language

@pytest.fixture
async def get_language(async_session_test):
    async def _get_language(id):
        async with async_session_test() as session:
            result = await session.execute(
                text("SELECT * FROM languages WHERE id = :id"), {"id": id}
            )
            return result.fetchone()
    return _get_language

@pytest.fixture
async def update_language(async_session_test):
    async def _update_language(id, **kwargs):
        async with async_session_test() as session:
            if kwargs:
                set_clause = ", ".join(
                    [f"{k} = :{k}" for k in kwargs.keys()]
                )
                query = f"UPDATE languages SET {set_clause} WHERE id = :id"
                kwargs["id"] = id
                await session.execute(text(query), kwargs)
                await session.commit()
    return _update_language

@pytest.fixture
async def delete_language(async_session_test):
    async def _delete_language(id):
        async with async_session_test() as session:
            await session.execute(
                text("DELETE FROM languages WHERE id = :id"), {"id": id}
            )
            await session.commit()
    return _delete_language

@pytest.fixture
async def create_user_language(async_session_test):
    async def _create_user_language(user_id, language_id):
        async with async_session_test() as session:
            user_language = UserLanguage(
                user_id=user_id, language_id=language_id
            )
            session.add(user_language)
            await session.commit()
    return _create_user_language

@pytest.fixture
async def delete_user_language(async_session_test):
    async def _delete_user_language(user_id, language_id):
        async with async_session_test() as session:
            await session.execute(
                text(
                    "DELETE FROM user_languages WHERE user_id = :user_id "
                    "AND language_id = :language_id"
                ),
                {"user_id": user_id, "language_id": language_id}
            )
            await session.commit()
    return _delete_user_language

@pytest.fixture
def get_data_user_social_media_link():
    return {
        "user_id": None,
        "title": "Facebook",
        "link": "https://facebook.com/ivan"
    }

@pytest.fixture
async def create_user_social_media_link(
    async_session_test, get_data_user_social_media_link
):
    async def _create_link(data=None):
        data = deepcopy(data or get_data_user_social_media_link)
        async with async_session_test() as session:
            link = UserSocialMediaLink(**data)
            session.add(link)
            await session.commit()
            await session.refresh(link)
            data["id"] = link.id
        return data
    return _create_link

@pytest.fixture
async def get_user_social_media_link(async_session_test):
    async def _get_link(id):
        async with async_session_test() as session:
            result = await session.execute(
                text("SELECT * FROM user_social_media_links WHERE id = :id"),
                {"id": id}
            )
            return result.fetchone()
    return _get_link

@pytest.fixture
async def update_user_social_media_link(async_session_test):
    async def _update_link(id, **kwargs):
        async with async_session_test() as session:
            if kwargs:
                set_clause = ", ".join(
                    [f"{k} = :{k}" for k in kwargs.keys()]
                )
                query = (
                    f"UPDATE user_social_media_links SET {set_clause} "
                    f"WHERE id = :id"
                )
                kwargs["id"] = id
                await session.execute(text(query), kwargs)
                await session.commit()
    return _update_link

@pytest.fixture
async def delete_user_social_media_link(async_session_test):
    async def _delete_link(id):
        async with async_session_test() as session:
            await session.execute(
                text("DELETE FROM user_social_media_links WHERE id = :id"),
                {"id": id}
            )
            await session.commit()
    return _delete_link

@pytest.fixture
def get_data_user_photo():
    return {
        "user_id": None,
        "url": "https://example.com/photo.jpg",
        "description": "My photo"
    }

@pytest.fixture
async def create_user_photo(async_session_test, get_data_user_photo):
    async def _create_photo(data=None):
        data = deepcopy(data or get_data_user_photo)
        async with async_session_test() as session:
            photo = UserPhoto(**data)
            session.add(photo)
            await session.commit()
            await session.refresh(photo)
            data["id"] = photo.id
        return data
    return _create_photo

@pytest.fixture
async def get_user_photo(async_session_test):
    async def _get_photo(id):
        async with async_session_test() as session:
            result = await session.execute(
                text("SELECT * FROM user_photos WHERE id = :id"), {"id": id}
            )
            return result.fetchone()
    return _get_photo

@pytest.fixture
async def update_user_photo(async_session_test):
    async def _update_photo(id, **kwargs):
        async with async_session_test() as session:
            if kwargs:
                set_clause = ", ".join(
                    [f"{k} = :{k}" for k in kwargs.keys()]
                )
                query = f"UPDATE user_photos SET {set_clause} WHERE id = :id"
                kwargs["id"] = id
                await session.execute(text(query), kwargs)
                await session.commit()
    return _update_photo

@pytest.fixture
async def delete_user_photo(async_session_test):
    async def _delete_photo(id):
        async with async_session_test() as session:
            await session.execute(
                text("DELETE FROM user_photos WHERE id = :id"), {"id": id}
            )
            await session.commit()
    return _delete_photo
