from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db_session
from src.user_profile.schemas import UserCreate
from src.user_profile.schemas import UserPhotoCreate
from src.user_profile.schemas import UserPhotoRead
from src.user_profile.schemas import UserPhotoUpdate
from src.user_profile.schemas import UserRead
from src.user_profile.schemas import UserSocialMediaLinkCreate
from src.user_profile.schemas import UserSocialMediaLinkRead
from src.user_profile.schemas import UserSocialMediaLinkUpdate
from src.user_profile.schemas import UserUpdate
from src.user_profile.service import _create_link
from src.user_profile.service import _create_photo
from src.user_profile.service import _create_user
from src.user_profile.service import _delete_link_by_id
from src.user_profile.service import _delete_photo_by_id
from src.user_profile.service import _delete_user
from src.user_profile.service import _get_all_links_by_user
from src.user_profile.service import _get_all_photos_by_user
from src.user_profile.service import _get_user_by_id
from src.user_profile.service import _update_link_by_id
from src.user_profile.service import _update_photo_by_id
from src.user_profile.service import _update_user


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_user_by_id(user_id, db_session)


@users_router.post("/", response_model=UserRead)
async def create_user(
    body: UserCreate, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _create_user(body, db_session)


@users_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    body: UserUpdate,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_user(body, user_id, db_session)


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _delete_user(user_id, db_session)


@users_router.get("/{user_id}/photos", response_model=List[UserPhotoRead])
async def get_all_photos_by_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_all_photos_by_user(user_id, db_session)


@users_router.post("/{user_id}/photos", response_model=UserPhotoRead)
async def create_photo(
    body: UserPhotoCreate,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _create_photo(body, user_id, db_session)


@users_router.patch("/{user_id}/photos/{photo_id}", response_model=UserPhotoRead)
async def update_photo(
    body: UserPhotoUpdate,
    user_id: UUID,
    photo_id: int,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_photo_by_id(body, user_id, photo_id, db_session)


@users_router.delete("/{user_id}/photos/{photo_id}")
async def delete_photo(
    user_id: UUID,
    photo_id: int,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _delete_photo_by_id(user_id, photo_id, db_session)


@users_router.get("/{user_id}/social-links", response_model=List[UserSocialMediaLinkRead])
async def get_all_social_links_by_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_all_links_by_user(user_id, db_session)


@users_router.post("/{user_id}/social-links", response_model=UserSocialMediaLinkRead)
async def create_social_link(
    body: UserSocialMediaLinkCreate,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _create_link(body, user_id, db_session)


@users_router.patch(
    "/{user_id}/social-links/{link_id}", response_model=UserSocialMediaLinkRead
)
async def update_social_link(
    body: UserSocialMediaLinkUpdate,
    user_id: UUID,
    link_id: int,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_link_by_id(body, user_id, link_id, db_session)


@users_router.delete("/{user_id}/social-links/{link_id}")
async def delete_social_link(
    user_id: UUID,
    link_id: int,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _delete_link_by_id(user_id, link_id, db_session)
