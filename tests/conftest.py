import asyncio
import datetime
import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import get_async_db_session
from src.main import app
from src.user_profile.dao import UserDAO
from src.user_profile.dao import UserPhotoDAO
from src.user_profile.dao import UserSocialMediaLinkDAO
from tests.config import TEST_DATABASE_URL

CLEAN_TABLES = ["users", "user_photos", "user_social_links"]


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_async_session():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def clean_test_db_tables(test_db_async_session: AsyncSession):
    async with test_db_async_session.begin():
        for table in CLEAN_TABLES:
            await test_db_async_session.execute(
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
    app.dependency_overrides[get_async_db_session] = get_test_db_async_session
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as async_client:
        yield async_client


@pytest.fixture
def data_user():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"Ivan_{unique_id}@mail.com",
        "name": "Ivan",
        "surname": "Ivanov",
        "date_of_birth": datetime.date(1990, 5, 15),
        "bio": "A handsome and smart man",
        "gender": "m",
        "country": "Russia",
        "city": "Moscow",
    }


@pytest.fixture
def data_user_photo():
    return {"url": "https://example.com/photo.jpg"}


@pytest.fixture
def data_user_social_link():
    return {"link": "https://t.me/example", "name": "Telegram"}


@pytest.fixture
async def create_user_fixture(test_db_async_session, data_user):
    async def _create_user(**kwargs):
        user_data = {**data_user, **kwargs}
        async with test_db_async_session() as session:
            user_dao = UserDAO(session)
            user = await user_dao.create_user(**user_data)
            await session.commit()
            return user

    return _create_user


@pytest.fixture
async def get_user_fixture(test_db_async_session):
    async def _get_user(user_id):
        async with test_db_async_session() as session:
            user_dao = UserDAO(session)
            return await user_dao.get_user_by_id(user_id)

    return _get_user


@pytest.fixture
async def update_user_fixture(test_db_async_session):
    async def _update_user(user_id, **kwargs):
        async with test_db_async_session() as session:
            user_dao = UserDAO(session)
            updated_user = await user_dao.update_user(user_id, **kwargs)
            await session.commit()
            return updated_user

    return _update_user


@pytest.fixture
async def delete_user_fixture(test_db_async_session):
    async def _delete_user(user_id):
        async with test_db_async_session() as session:
            user_dao = UserDAO(session)
            deleted_user = await user_dao.delete_user_by_id(user_id)
            await session.commit()
            return deleted_user

    return _delete_user


@pytest.fixture
async def create_user_photo_fixture(
    test_db_async_session, data_user_photo, create_user_fixture
):
    async def _create_photo(user_id=None, **kwargs):
        async with test_db_async_session() as session:
            photo_data = {**data_user_photo, **kwargs}
            photo_dao = UserPhotoDAO(session)
            uid = user_id or (await create_user_fixture()).id
            photo = await photo_dao.create_photo(user_id=uid, **photo_data)
            await session.commit()
            return photo

    return _create_photo


@pytest.fixture
async def get_user_photo_fixture(test_db_async_session):
    async def _get_photo(user_id):
        async with test_db_async_session() as session:
            photo_dao = UserPhotoDAO(session)
            photos = await photo_dao.get_all_photos_by_user(user_id)
            return photos[0] if photos else None

    return _get_photo


@pytest.fixture
async def update_user_photo_fixture(test_db_async_session):
    async def _update_photo(photo_id, **kwargs):
        async with test_db_async_session() as session:
            photo_dao = UserPhotoDAO(session)
            updated_photo = await photo_dao.update_photo_by_id(photo_id, **kwargs)
            await session.commit()
            return updated_photo

    return _update_photo


@pytest.fixture
async def delete_user_photo_fixture(test_db_async_session):
    async def _delete_photo(photo_id):
        async with test_db_async_session() as session:
            photo_dao = UserPhotoDAO(session)
            deleted_photo = await photo_dao.delete_photo_by_id(photo_id)
            await session.commit()
            return deleted_photo

    return _delete_photo


@pytest.fixture
async def create_user_social_link_fixture(
    test_db_async_session, data_user_social_link, create_user_fixture
):
    async def _create_link(user_id=None, **kwargs):
        async with test_db_async_session() as session:
            link_data = {**data_user_social_link, **kwargs}
            link_dao = UserSocialMediaLinkDAO(session)
            uid = user_id or (await create_user_fixture()).id
            link = await link_dao.create_link(user_id=uid, **link_data)
            await session.commit()
            return link

    return _create_link


@pytest.fixture
async def get_user_social_link_fixture(test_db_async_session):
    async def _get_link(user_id):
        async with test_db_async_session() as session:
            link_dao = UserSocialMediaLinkDAO(session)
            links = await link_dao.get_all_links_by_user(user_id)
            return links[0] if links else None

    return _get_link


@pytest.fixture
async def update_user_social_link_fixture(test_db_async_session):
    async def _update_link(link_id, **kwargs):
        async with test_db_async_session() as session:
            link_dao = UserSocialMediaLinkDAO(session)
            updated_link = await link_dao.update_link_by_id(link_id, **kwargs)
            await session.commit()
            return updated_link

    return _update_link


@pytest.fixture
async def delete_user_social_link_fixture(test_db_async_session):
    async def _delete_link(link_id):
        async with test_db_async_session() as session:
            link_dao = UserSocialMediaLinkDAO(session)
            deleted_link = await link_dao.delete_link_by_id(link_id)
            await session.commit()
            return deleted_link

    return _delete_link
