from typing import List
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_profile.models import Language
from src.user_profile.models import User
from src.user_profile.models import UserLanguage
from src.user_profile.models import UserPhoto
from src.user_profile.models import UserSocialMediaLink


class UserDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_new_user(
        self,
        username: str,
        email: str,
        bio: str,
        gender: str,
        country: str,
        city: str,
    ) -> User:
        new_user = User(
            username=username,
            email=email,
            bio=bio,
            gender=gender,
            country=country,
            city=city,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_user_by_id(self, id: UUID) -> Optional[User]:
        db_query = select(User).where(User.id == id)
        db_response = await self.db_session.execute(db_query)
        user = db_response.scalars().first()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        db_query = select(User).where(User.email == email)
        db_response = await self.db_session.execute(db_query)
        user = db_response.scalars().first()
        return user

    async def delete_user(self, id: UUID) -> Optional[User]:
        db_query = (
            delete(User)
            .where(User.id == id)
            .returning(User)
        )
        db_response = await self.db_session.execute(db_query)
        deleted_user = db_response.fetchone()
        return deleted_user[0] if deleted_user is not None else None

    async def update_user(self, id: UUID, **kwargs) -> Optional[User]:
        db_query = (
            update(User)
            .where(User.id == id)
            .values(**kwargs)
            .returning(User)
        )
        db_response = await self.db_session.execute(db_query)
        updated_user = db_response.fetchone()
        return updated_user[0] if updated_user is not None else None


class UserSocialMediaLinkDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_link(
        self,
        user_id: UUID,
        title: str,
        link: str,
    ) -> UserSocialMediaLink:
        new_link = UserSocialMediaLink(
            user_id=user_id,
            title=title,
            link=link,
        )
        self.db_session.add(new_link)
        try:
            await self.db_session.flush()
        except IntegrityError as e:
            if (
                "ForeignKeyViolationError" in str(e)
                or "foreign key constraint" in str(e)
                or "violates foreign key constraint" in str(e)
            ):
                raise HTTPException(status_code=422, detail="Invalid user ID")
            raise
        return new_link

    async def delete_link_by_id(self, link_id: int) -> Optional[UserSocialMediaLink]:
        db_query = (
            delete(UserSocialMediaLink)
            .where(UserSocialMediaLink.id == link_id)
            .returning(UserSocialMediaLink)
        )
        db_response = await self.db_session.execute(db_query)
        deleted_link = db_response.fetchone()
        return deleted_link[0] if deleted_link is not None else None

    async def get_links_by_user(self, user_id: UUID) -> List[UserSocialMediaLink]:
        db_query = select(UserSocialMediaLink).where(
            UserSocialMediaLink.user_id == user_id
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def get_link_id(self, id: int) -> Optional[UserSocialMediaLink]:
        db_query = select(UserSocialMediaLink).where(UserSocialMediaLink.id == id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().first()

    async def update_link(self, id: int, **kwargs) -> Optional[UserSocialMediaLink]:
        db_query = (
            update(UserSocialMediaLink)
            .where(UserSocialMediaLink.id == id)
            .values(**kwargs)
            .returning(UserSocialMediaLink)
        )
        db_response = await self.db_session.execute(db_query)
        updated_link = db_response.fetchone()
        return updated_link[0] if updated_link is not None else None


class UserPhotoDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_photo(
        self,
        user_id: UUID,
        url: str,
        description: str,
    ) -> UserPhoto:
        photo = UserPhoto(
            user_id=user_id,
            url=url,
            description=description,
        )
        self.db_session.add(photo)
        try:
            await self.db_session.flush()
        except IntegrityError as e:
            if (
                "ForeignKeyViolationError" in str(e)
                or "foreign key constraint" in str(e)
                or "violates foreign key constraint" in str(e)
            ):
                raise HTTPException(status_code=422, detail="Invalid user ID")
            raise
        return photo

    async def delete_photo_by_id(self, id: int) -> Optional[UserPhoto]:
        db_query = (
            delete(UserPhoto)
            .where(UserPhoto.id == id)
            .returning(UserPhoto)
        )
        db_response = await self.db_session.execute(db_query)
        deleted_photo = db_response.fetchone()
        return deleted_photo[0] if deleted_photo is not None else None

    async def get_photos_by_user(self, user_id: UUID) -> List[UserPhoto]:
        db_query = select(UserPhoto).where(UserPhoto.user_id == user_id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def get_photo_by_id(self, id: int) -> Optional[UserPhoto]:
        db_query = select(UserPhoto).where(UserPhoto.id == id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().first()

    async def update_photo(self, id: int, **kwargs) -> Optional[UserPhoto]:
        db_query = (
            update(UserPhoto)
            .where(UserPhoto.id == id)
            .values(**kwargs)
            .returning(UserPhoto)
        )
        db_response = await self.db_session.execute(db_query)
        updated_photo = db_response.fetchone()
        return updated_photo[0] if updated_photo is not None else None


class LanguageDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_language(self, name: str) -> Language:
        language = Language(name=name)
        self.db_session.add(language)
        await self.db_session.flush()
        return language

    async def delete_language_by_id(self, id: int) -> Optional[Language]:
        db_query = (
            delete(Language)
            .where(Language.id == id)
            .returning(Language)
        )
        db_response = await self.db_session.execute(db_query)
        deleted_language = db_response.fetchone()
        return deleted_language[0] if deleted_language is not None else None

    async def get_all_languages(self) -> List[Language]:
        db_query = select(Language)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def get_language_by_id(self, id: int) -> Optional[Language]:
        db_query = select(Language).where(Language.id == id)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().first()

    async def get_language_by_name(self, name: str) -> Optional[Language]:
        db_query = select(Language).where(Language.name == name)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().first()

    async def update_language(self, id: int, **kwargs) -> Optional[Language]:
        db_query = (
            update(Language)
            .where(Language.id == id)
            .values(**kwargs)
            .returning(Language)
        )
        db_response = await self.db_session.execute(db_query)
        updated_language = db_response.fetchone()
        return updated_language[0] if updated_language is not None else None


class UserLanguageDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user_id: UUID, language_id: int) -> None:
        link = UserLanguage(user_id=user_id, language_id=language_id)
        self.db_session.add(link)
        await self.db_session.flush()

    async def delete(self, user_id: UUID, language_id: int) -> bool:
        query = delete(UserLanguage).where(
            and_(
                UserLanguage.user_id == user_id,
                UserLanguage.language_id == language_id,
            )
        )
        result = await self.db_session.execute(query)
        return result.rowcount > 0

    async def get_languages_by_user(self, user_id: UUID) -> List[UserLanguage]:
        query = select(UserLanguage).where(UserLanguage.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_users_by_language(self, language_id: int) -> List[UserLanguage]:
        query = select(UserLanguage).where(UserLanguage.language_id == language_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
