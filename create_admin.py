import asyncio
import os
import uuid
from datetime import date

import bcrypt
from dotenv import load_dotenv

from src.auth.models import RefreshToken  # noqa: F401
from src.database import async_session
from src.models import Base  # noqa: F401
from src.user_profile.models import User


async def create_admin_user():
    load_dotenv("env/.env.admin")

    admin_data = {
        "email": os.getenv("ADMIN_EMAIL"),
        "password": os.getenv("ADMIN_PASSWORD"),
        "name": os.getenv("ADMIN_NAME"),
        "surname": os.getenv("ADMIN_SURNAME"),
        "date_of_birth": date.fromisoformat(os.getenv("ADMIN_DATE_OF_BIRTH")),
        "bio": os.getenv("ADMIN_BIO"),
        "gender": os.getenv("ADMIN_GENDER"),
        "country": os.getenv("ADMIN_COUNTRY"),
        "city": os.getenv("ADMIN_CITY"),
    }

    async with async_session() as db_session:
        async with db_session.begin():
            from sqlalchemy import func, select

            admin_count = await db_session.execute(
                select(func.count(User.id)).where(User.role == "admin")
            )
            admin_count = admin_count.scalar()

            if admin_count > 0:
                print("Админ уже существует в системе!")
                print("В системе может быть только один админ")
                return

    try:
        password_hash = bcrypt.hashpw(
            admin_data["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        admin_user = User(
            id=uuid.uuid4(),
            email=admin_data["email"],
            hash_password=password_hash,
            name=admin_data["name"],
            surname=admin_data["surname"],
            date_of_birth=admin_data["date_of_birth"],
            bio=admin_data["bio"],
            gender=admin_data["gender"],
            country=admin_data["country"],
            city=admin_data["city"],
            role="admin",
        )

        async with async_session() as db_session:
            async with db_session.begin():
                db_session.add(admin_user)
                await db_session.flush()

    except Exception as e:
        print(f"Ошибка при создании админа: {e}")
        raise


if __name__ == "__main__":
    print("Создание пользователя с ролью админа...")
    asyncio.run(create_admin_user())
