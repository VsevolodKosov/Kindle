from typing import List
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.user_profile.dao import LanguageDAO
from src.user_profile.dao import UserDAO
from src.user_profile.dao import UserLanguageDAO
from src.user_profile.dao import UserPhotoDAO
from src.user_profile.dao import UserSocialMediaLinkDAO
from src.user_profile.schemas import LanguageCreate
from src.user_profile.schemas import LanguageRead
from src.user_profile.schemas import UserCreate
from src.user_profile.schemas import UserLanguageCreate
from src.user_profile.schemas import UserLanguageRead
from src.user_profile.schemas import UserPhotoCreate
from src.user_profile.schemas import UserPhotoRead
from src.user_profile.schemas import UserRead
from src.user_profile.schemas import UserSocialMediaLinkCreate
from src.user_profile.schemas import UserSocialMediaLinkRead


async def create_user(data: UserCreate, db_session: AsyncSession) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        new_user = await user_dao.create_new_user(
            username=data.username,
            email=data.email,
            bio=data.bio,
            gender=data.gender,
            country=data.country,
            city=data.city,
        )
    return UserRead.from_orm_obj(new_user)


async def get_user(id: UUID, db_session: AsyncSession) -> Optional[UserRead]:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        user = await user_dao.get_user_by_id(id=id)
    return UserRead.from_orm_obj(user) if user else None


async def update_user(
    updated_user_params: dict, id: UUID, db_session: AsyncSession
) -> Optional[UserRead]:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        updated_user = await user_dao.update_user(id=id, **updated_user_params)
    return UserRead.from_orm_obj(updated_user) if updated_user else None


async def delete_user(id: UUID, db_session: AsyncSession) -> Optional[UserRead]:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        deleted_user = await user_dao.delete_user(id=id)
    return UserRead.from_orm_obj(deleted_user) if deleted_user else None


async def create_photo(
    data: UserPhotoCreate, db_session: AsyncSession
 ) -> UserPhotoRead:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        new_photo = await photo_dao.create_photo(
            user_id=data.user_id,
            url=data.url,
            description=data.description,
        )
    return UserPhotoRead.from_orm_obj(new_photo)


async def get_photos_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserPhotoRead]:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        photos = await photo_dao.get_photos_by_user(user_id=user_id)
    return [UserPhotoRead.from_orm_obj(photo) for photo in photos]


async def delete_photo(
    photo_id: int, db_session: AsyncSession
) -> Optional[UserPhotoRead]:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        deleted_photo = await photo_dao.delete_photo_by_id(photo_id)
    return UserPhotoRead.from_orm_obj(deleted_photo) if deleted_photo else None


async def create_social_link(
    data: UserSocialMediaLinkCreate, db_session: AsyncSession
) -> UserSocialMediaLinkRead:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        new_link = await link_dao.create_link(
            user_id=data.user_id,
            title=data.title,
            link=data.link,
        )
    return UserSocialMediaLinkRead.from_orm_obj(new_link)


async def get_links_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserSocialMediaLinkRead]:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        links = await link_dao.get_links_by_user(user_id)
    return [UserSocialMediaLinkRead.from_orm_obj(link) for link in links]


async def delete_social_link(
    link_id: int, db_session: AsyncSession
) -> Optional[UserSocialMediaLinkRead]:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        deleted_link = await link_dao.delete_link_by_id(link_id)
    return UserSocialMediaLinkRead.from_orm_obj(deleted_link) if deleted_link else None


async def create_language(
    data: LanguageCreate, db_session: AsyncSession
) -> LanguageRead:
    async with db_session.begin():
        language_dao = LanguageDAO(db_session)
        new_language = await language_dao.create_language(name=data.name)
    return LanguageRead.from_orm_obj(new_language)


async def get_all_languages(db_session: AsyncSession) -> List[LanguageRead]:
    async with db_session.begin():
        language_dao = LanguageDAO(db_session)
        languages = await language_dao.get_all_languages()
    return [LanguageRead.from_orm_obj(lang) for lang in languages]


async def delete_language(
    language_id: int, db_session: AsyncSession
) -> Optional[LanguageRead]:
    async with db_session.begin():
        language_dao = LanguageDAO(db_session)
        deleted_lang = await language_dao.delete_language_by_id(language_id)
    return LanguageRead.from_orm_obj(deleted_lang) if deleted_lang else None


async def add_language_to_user(
    data: UserLanguageCreate, db_session: AsyncSession
) -> UserLanguageRead:
    async with db_session.begin():
        user_lang_dao = UserLanguageDAO(db_session)
        await user_lang_dao.create(user_id=data.user_id, language_id=data.language_id)
    return UserLanguageRead(user_id=data.user_id, language_id=data.language_id)


async def get_languages_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserLanguageRead]:
    async with db_session.begin():
        user_lang_dao = UserLanguageDAO(db_session)
        user_langs = await user_lang_dao.get_languages_by_user(user_id)
    return [
        UserLanguageRead(user_id=ul.user_id, language_id=ul.language_id)
        for ul in user_langs
    ]


async def remove_language_from_user(
    user_id: UUID, language_id: int, db_session: AsyncSession
) -> None:
    async with db_session.begin():
        user_lang_dao = UserLanguageDAO(db_session)
        await user_lang_dao.delete(user_id=user_id, language_id=language_id)
