from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_async_db_session
from src.user_profile.schemas import (
    UserPhotoCreate,
    UserPhotoRead,
    UserPhotoUpdate,
    UserRead,
    UserSocialMediaLinkCreate,
    UserSocialMediaLinkRead,
    UserSocialMediaLinkUpdate,
    UserUpdate,
)
from src.user_profile.service import (
    _create_link,
    _create_photo,
    _delete_link_by_id,
    _delete_photo_by_id,
    _delete_user,
    _get_all_links_by_user,
    _get_all_photos_by_user,
    _get_user_by_id,
    _update_link_by_id,
    _update_photo_by_id,
    _update_user,
)

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_user_by_id(user_id, db_session)


@users_router.patch("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(
    body: UserUpdate,
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_user(body, user_id, current_user, db_session)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    await _delete_user(user_id, current_user, db_session)


@users_router.get(
    "/{user_id}/photos",
    response_model=List[UserPhotoRead],
    status_code=status.HTTP_200_OK,
)
async def get_all_photos_by_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_all_photos_by_user(user_id, db_session)


@users_router.post(
    "/{user_id}/photos",
    response_model=UserPhotoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_photo(
    body: UserPhotoCreate,
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _create_photo(body, user_id, current_user, db_session)


@users_router.patch(
    "/{user_id}/photos/{photo_id}",
    response_model=UserPhotoRead,
    status_code=status.HTTP_200_OK,
)
async def update_photo(
    body: UserPhotoUpdate,
    user_id: UUID,
    photo_id: int,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_photo_by_id(body, user_id, photo_id, current_user, db_session)


@users_router.delete(
    "/{user_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_photo(
    user_id: UUID,
    photo_id: int,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    await _delete_photo_by_id(user_id, photo_id, current_user, db_session)


@users_router.get(
    "/{user_id}/social-links",
    response_model=List[UserSocialMediaLinkRead],
    status_code=status.HTTP_200_OK,
)
async def get_all_social_links_by_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_db_session)
):
    return await _get_all_links_by_user(user_id, db_session)


@users_router.post(
    "/{user_id}/social-links",
    response_model=UserSocialMediaLinkRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_social_link(
    body: UserSocialMediaLinkCreate,
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _create_link(body, user_id, current_user, db_session)


@users_router.patch(
    "/{user_id}/social-links/{link_id}",
    response_model=UserSocialMediaLinkRead,
    status_code=status.HTTP_200_OK,
)
async def update_social_link(
    body: UserSocialMediaLinkUpdate,
    user_id: UUID,
    link_id: int,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _update_link_by_id(body, user_id, link_id, current_user, db_session)


@users_router.delete(
    "/{user_id}/social-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_social_link(
    user_id: UUID,
    link_id: int,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    await _delete_link_by_id(user_id, link_id, current_user, db_session)
