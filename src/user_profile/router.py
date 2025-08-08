from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_async_session
from src.user_profile import service
from src.user_profile.dependencies import get_user_languages
from src.user_profile.dependencies import validate_email_unique
from src.user_profile.dependencies import validate_email_unique_for_update
from src.user_profile.dependencies import validate_language_create_payload
from src.user_profile.dependencies import validate_language_exists
from src.user_profile.dependencies import validate_photo_exists
from src.user_profile.dependencies import validate_social_link_exists
from src.user_profile.dependencies import validate_user_exists
from src.user_profile.schemas import LanguageCreate
from src.user_profile.schemas import LanguageRead
from src.user_profile.schemas import LanguageUpdate
from src.user_profile.schemas import UserCreate
from src.user_profile.schemas import UserLanguageCreate
from src.user_profile.schemas import UserLanguageRead
from src.user_profile.schemas import UserPhotoCreate
from src.user_profile.schemas import UserPhotoRead
from src.user_profile.schemas import UserPhotoUpdate
from src.user_profile.schemas import UserRead
from src.user_profile.schemas import UserSocialMediaLinkCreate
from src.user_profile.schemas import UserSocialMediaLinkRead
from src.user_profile.schemas import UserSocialMediaLinkUpdate
from src.user_profile.schemas import UserUpdate

user_profile_router = APIRouter()



@user_profile_router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user: UserRead = Depends(validate_user_exists),
):
    return user


@user_profile_router.post("/", response_model=UserRead)
async def create_user(
    data: UserCreate,
    db_session: AsyncSession = Depends(get_db_async_session),
):

    await validate_email_unique(data.email, db_session)
    new_user = await service.create_user(data, db_session)
    return new_user


@user_profile_router.patch("/", response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    user: UserRead = Depends(validate_user_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):

    if user_update.email:
        await validate_email_unique_for_update(user_update.email, user.id, db_session)

    updated_user = await service.update_user(
        user_update.model_dump(exclude_unset=True),
        user.id,
        db_session,
    )
    return updated_user


@user_profile_router.delete("/", response_model=UserRead)
async def delete_user(
    user: UserRead = Depends(validate_user_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    deleted_user = await service.delete_user(user.id, db_session)
    return deleted_user




@user_profile_router.get("/photos/{photo_id}", response_model=UserPhotoRead)
async def read_photo(
    photo: UserPhotoRead = Depends(validate_photo_exists),
):
    return photo


@user_profile_router.post("/photos", response_model=UserPhotoRead)
async def create_photo(
    data: UserPhotoCreate,
    db_session: AsyncSession = Depends(get_db_async_session),
):
    new_photo = await service.create_photo(data, db_session)
    return new_photo


@user_profile_router.patch("/photos/{photo_id}", response_model=UserPhotoRead)
async def update_photo(
    photo_update: UserPhotoUpdate,
    photo: UserPhotoRead = Depends(validate_photo_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    updated_photo = await service.update_photo(
        photo.id,
        photo_update.model_dump(exclude_unset=True),
        db_session,
    )
    return updated_photo


@user_profile_router.delete("/photos/{photo_id}", response_model=UserPhotoRead)
async def delete_photo(
    photo: UserPhotoRead = Depends(validate_photo_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    deleted_photo = await service.delete_photo(photo.id, db_session)
    return deleted_photo




@user_profile_router.get(
    "/social-links/{link_id}", response_model=UserSocialMediaLinkRead
)
async def read_social_link(
    link: UserSocialMediaLinkRead = Depends(validate_social_link_exists),
):
    return link


@user_profile_router.post("/social-links", response_model=UserSocialMediaLinkRead)
async def create_social_link(
    data: UserSocialMediaLinkCreate,
    db_session: AsyncSession = Depends(get_db_async_session),
):
    new_link = await service.create_social_link(data, db_session)
    return new_link


@user_profile_router.patch(
    "/social-links/{link_id}", response_model=UserSocialMediaLinkRead
)
async def update_social_link(
    link_update: UserSocialMediaLinkUpdate,
    link: UserSocialMediaLinkRead = Depends(validate_social_link_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    updated_link = await service.update_social_link(
        link.id,
        link_update.model_dump(exclude_unset=True),
        db_session,
    )
    return updated_link


@user_profile_router.delete(
    "/social-links/{link_id}", response_model=UserSocialMediaLinkRead
)
async def delete_social_link(
    link: UserSocialMediaLinkRead = Depends(validate_social_link_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    deleted_link = await service.delete_social_link(link.id, db_session)
    return deleted_link




@user_profile_router.get("/languages/", response_model=List[LanguageRead])
async def list_languages(db_session: AsyncSession = Depends(get_db_async_session)):
    return await service.get_all_languages(db_session)



@user_profile_router.patch("/languages/")
async def update_language_missing_id():
    raise HTTPException(status_code=422, detail="Invalid language id")


@user_profile_router.delete("/languages/")
async def delete_language_missing_id():
    raise HTTPException(status_code=422, detail="Invalid language id")


@user_profile_router.get("/languages/{language_id}", response_model=LanguageRead)
async def read_language(
    language: LanguageRead = Depends(validate_language_exists),
):
    return language


@user_profile_router.post("/languages/", response_model=LanguageRead)
async def create_language(
    data: LanguageCreate,
    db_session: AsyncSession = Depends(get_db_async_session),
    _: None = Depends(validate_language_create_payload),
):
    new_language = await service.create_language(data, db_session)
    return new_language


@user_profile_router.patch("/languages/{language_id}", response_model=LanguageRead)
async def update_language(
    language_update: LanguageUpdate,
    language: LanguageRead = Depends(validate_language_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    update_data = language_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="No data provided for update")

    updated_language = await service.update_language(
        language.id,
        update_data,
        db_session,
    )
    return updated_language


@user_profile_router.delete("/languages/{language_id}", response_model=LanguageRead)
async def delete_language(
    language: LanguageRead = Depends(validate_language_exists),
    db_session: AsyncSession = Depends(get_db_async_session),
):
    deleted_language = await service.delete_language(language.id, db_session)
    return deleted_language




@user_profile_router.get(
    "/{user_id}/languages", response_model=List[UserLanguageRead]
)
async def read_user_languages(
    user_languages: List[UserLanguageRead] = Depends(get_user_languages),
):
    return user_languages


@user_profile_router.post(
    "/{user_id}/languages", response_model=UserLanguageRead
)
async def add_language_to_user(
    data: UserLanguageCreate,
    db_session: AsyncSession = Depends(get_db_async_session),
):
    user_language = await service.add_language_to_user(data, db_session)
    return user_language


@user_profile_router.delete(
    "/{user_id}/languages/{language_id}", status_code=204
)
async def remove_language_from_user(
    user_id: str,
    language_id: int,
    db_session: AsyncSession = Depends(get_db_async_session),
):
    await service.remove_language_from_user(
        user_id,
        language_id,
        db_session,
    )
    return None
