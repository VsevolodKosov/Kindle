import asyncio
import uuid
from typing import Any, AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import get_async_db_session
from src.main import app
from tests.config import TEST_DATABASE_URL

CLEAN_TABLES = ["users", "user_photo", "user_social_media_links", "refresh_tokens"]


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
    }


@pytest.fixture
def data_user_photo() -> Dict[str, str]:
    return {"url": "https://example.com/photo.jpg"}


@pytest.fixture
def data_user_social_link() -> Dict[str, str]:
    return {"link": "https://t.me/example", "name": "Telegram"}
