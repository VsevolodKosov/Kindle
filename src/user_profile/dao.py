from datetime import date
from typing import List
from typing import Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_profile.models import User
from src.user_profile.models import UserPhoto
from src.user_profile.models import UserSocialMediaLinks


class UserDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        email: str,
        name: str,
        surname: str,
        date_of_birth: date,
        bio: str,
        gender: str,
        country: str,
        city: str,
    ) -> User:
        try:
            new_user = User(
                email=email,
                name=name,
                surname=surname,
                date_of_birth=date_of_birth,
                bio=bio,
                gender=gender,
                country=country,
                city=city,
            )
            self.db_session.add(new_user)
            await self.db_session.flush()
            return new_user

        except IntegrityError as error:
            if "unique constraint" in str(error.orig):
                raise ValueError("User with this email already exists")

    async def get_user_by_id(self, id: UUID) -> Optional[User]:
        db_query = select(User).where(User.id == id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()

    async def update_user(self, id: UUID, **kwargs) -> Optional[User]:
        try:
            db_query = update(User).where(User.id == id).values(**kwargs).returning(User)
            db_response = await self.db_session.execute(db_query)
            return db_response.scalar_one_or_none()

        except IntegrityError as error:
            if "unique constraint" in str(error.orig):
                raise ValueError("User with this email already exists")

    async def delete_user_by_id(self, id: UUID) -> Optional[User]:
        db_query = delete(User).where(User.id == id).returning(User)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()


class UserPhotoDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_photo(self, user_id: UUID, url: str) -> UserPhoto:
        new_photo = UserPhoto(user_id=user_id, url=url)
        self.db_session.add(new_photo)
        await self.db_session.flush()
        return new_photo

    async def get_all_photos_by_user(self, user_id: UUID) -> List[UserPhoto]:
        db_query = select(UserPhoto).where(UserPhoto.user_id == user_id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def update_photo_by_id(self, photo_id: int, **kwargs) -> Optional[UserPhoto]:
        if not kwargs:
            return None

        db_query = (
            update(UserPhoto)
            .where(UserPhoto.id == photo_id)
            .values(**kwargs)
            .returning(UserPhoto)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()

    async def delete_photo_by_id(self, photo_id: int) -> Optional[UserPhoto]:
        db_query = delete(UserPhoto).where(UserPhoto.id == photo_id).returning(UserPhoto)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()


class UserSocialMediaLinkDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_link(
        self, user_id: UUID, link: str, name: str
    ) -> UserSocialMediaLinks:
        new_link = UserSocialMediaLinks(user_id=user_id, link=link, name=name)
        self.db_session.add(new_link)
        await self.db_session.flush()
        return new_link

    async def get_all_links_by_user(self, user_id: UUID) -> List[UserSocialMediaLinks]:
        db_query = select(UserSocialMediaLinks).where(
            UserSocialMediaLinks.user_id == user_id
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def update_link_by_id(
        self, link_id: int, **kwargs
    ) -> Optional[UserSocialMediaLinks]:
        if not kwargs:
            return None

        db_query = (
            update(UserSocialMediaLinks)
            .where(UserSocialMediaLinks.id == link_id)
            .values(**kwargs)
            .returning(UserSocialMediaLinks)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()

    async def delete_link_by_id(self, link_id: int) -> Optional[UserSocialMediaLinks]:
        db_query = (
            delete(UserSocialMediaLinks)
            .where(UserSocialMediaLinks.id == link_id)
            .returning(UserSocialMediaLinks)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()
