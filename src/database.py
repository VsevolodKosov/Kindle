from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        db_session: AsyncSession = async_session()
        yield db_session
    finally:
        db_session.close()
