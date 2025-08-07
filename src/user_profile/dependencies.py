from typing import List
from typing import Optional
from typing import TypeVar
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_async_session
from src.user_profile import service
from src.user_profile.schemas import LanguageRead
from src.user_profile.schemas import UserLanguageRead
from src.user_profile.schemas import UserPhotoRead
from src.user_profile.schemas import UserRead
from src.user_profile.schemas import UserSocialMediaLinkRead

T = TypeVar('T')

async def validate_exists(
    item: Optional[T],
    item_name: str,
) -> T:
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_name} not found")
    return item


async def get_user(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> Optional[UserRead]:
    return await service.get_user(user_id, db_session)


async def validate_user_exists(
    user: Optional[UserRead] = Depends(get_user),
) -> UserRead:
    return await validate_exists(user, "User")


async def validate_email_unique(
    email: str,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> None:
    existing_user = await service.get_user_by_email(email, db_session)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )


async def get_photo(
    photo_id: int,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> Optional[UserPhotoRead]:
    return await service.get_photo_by_id(photo_id, db_session)


async def validate_photo_exists(
    photo: Optional[UserPhotoRead] = Depends(get_photo),
) -> UserPhotoRead:
    return await validate_exists(photo, "Photo")


async def get_social_link(
    link_id: int,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> Optional[UserSocialMediaLinkRead]:
    return await service.get_link_by_id(link_id, db_session)


async def validate_social_link_exists(
    link: Optional[UserSocialMediaLinkRead] = Depends(get_social_link),
) -> UserSocialMediaLinkRead:
    return await validate_exists(link, "Social link")


async def get_language(
    language_id: int,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> Optional[LanguageRead]:
    return await service.get_language_by_id(language_id, db_session)


async def validate_language_exists(
    language: Optional[LanguageRead] = Depends(get_language),
) -> LanguageRead:
    return await validate_exists(language, "Language")


async def get_user_languages(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_db_async_session),
) -> List[UserLanguageRead]:
    return await service.get_languages_by_user(user_id, db_session)


async def validate_user_language_exists(
    language_id: int,
    user_languages: List[UserLanguageRead] = Depends(get_user_languages),
) -> None:
    if not any(ul.language_id == language_id for ul in user_languages):
        raise HTTPException(status_code=404, detail="Language not assigned to user")


async def verify_language_not_assigned(
    language_id: int,
    user_languages: List[UserLanguageRead] = Depends(get_user_languages),
) -> None:
    if any(ul.language_id == language_id for ul in user_languages):
        raise HTTPException(status_code=400, detail="Language already assigned to user")
