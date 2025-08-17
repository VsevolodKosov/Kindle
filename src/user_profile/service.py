from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_profile.dao import UserDAO, UserPhotoDAO, UserSocialMediaLinkDAO
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
from src.user_profile.utils import (
    check_user_delete_permission,
    check_user_edit_permission,
)


async def _get_user_by_id(id: UUID, db_session: AsyncSession) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        user = await user_dao.get_user_by_id(id)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )
        return UserRead.from_orm_obj(user)


async def _update_user(
    body: UserUpdate, id: UUID, current_user: UserRead, db_session: AsyncSession
) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        target_user = await user_dao.get_user_by_id(id)

        if target_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )

        check_user_edit_permission(current_user, id, target_user.role)

        update_data = {k: v for k, v in body.model_dump(exclude_unset=True).items()}

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        try:
            updated_user = await user_dao.update_user(id, **update_data)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))

        if updated_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )

        return UserRead.from_orm_obj(updated_user)


async def _delete_user(
    id: UUID, current_user: UserRead, db_session: AsyncSession
) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        target_user = await user_dao.get_user_by_id(id)

        if target_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )

        check_user_delete_permission(current_user, id, target_user.role)

        deleted_user = await user_dao.delete_user_by_id(id)
        if deleted_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )
        return UserRead.from_orm_obj(deleted_user)


async def _create_photo(
    body: UserPhotoCreate, user_id: UUID, current_user: UserRead, db_session: AsyncSession
) -> UserPhotoRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        photo = await photo_dao.create_photo(user_id=user_id, url=body.url)
        return UserPhotoRead.from_orm_obj(photo)


async def _get_all_photos_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserPhotoRead]:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        user = await user_dao.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} doesn't exist"
            )

        photo_dao = UserPhotoDAO(db_session)
        photos = await photo_dao.get_all_photos_by_user(user_id)
        return [UserPhotoRead.from_orm_obj(photo) for photo in photos]


async def _delete_photo_by_id(
    user_id: UUID, photo_id: int, current_user: UserRead, db_session: AsyncSession
) -> UserPhotoRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        deleted_photo = await photo_dao.delete_photo_by_id(photo_id)

        if deleted_photo is None:
            raise HTTPException(
                status_code=404, detail=f"Photo with id {photo_id} doesn't exist"
            )

        return UserPhotoRead.from_orm_obj(deleted_photo)


async def _update_photo_by_id(
    body: UserPhotoUpdate,
    user_id: UUID,
    photo_id: int,
    current_user: UserRead,
    db_session: AsyncSession,
) -> UserPhotoRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        update_data = {
            k: v for k, v in body.model_dump(exclude_unset=True).items() if k != "id"
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        updated_photo = await photo_dao.update_photo_by_id(
            photo_id=photo_id, **update_data
        )
        if updated_photo is None:
            raise HTTPException(
                status_code=404, detail=f"Photo with id {photo_id} doesn't exist"
            )

        return UserPhotoRead.from_orm_obj(updated_photo)


async def _create_link(
    body: UserSocialMediaLinkCreate,
    user_id: UUID,
    current_user: UserRead,
    db_session: AsyncSession,
) -> UserSocialMediaLinkRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        link = await link_dao.create_link(user_id=user_id, link=body.link, name=body.name)
        return UserSocialMediaLinkRead.from_orm_obj(link)


async def _get_all_links_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserSocialMediaLinkRead]:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        user = await user_dao.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} doesn't exist"
            )

        link_dao = UserSocialMediaLinkDAO(db_session)
        links = await link_dao.get_all_links_by_user(user_id)
        return [UserSocialMediaLinkRead.from_orm_obj(link) for link in links]


async def _update_link_by_id(
    body: UserSocialMediaLinkUpdate,
    user_id: UUID,
    link_id: int,
    current_user: UserRead,
    db_session: AsyncSession,
) -> UserSocialMediaLinkRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        update_data = {
            k: v for k, v in body.model_dump(exclude_unset=True).items() if k != "id"
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        updated_link = await link_dao.update_link_by_id(link_id=link_id, **update_data)

        if updated_link is None:
            raise HTTPException(
                status_code=404, detail=f"Link with id {link_id} doesn't exist"
            )

        return UserSocialMediaLinkRead.from_orm_obj(updated_link)


async def _delete_link_by_id(
    user_id: UUID, link_id: int, current_user: UserRead, db_session: AsyncSession
) -> UserSocialMediaLinkRead:
    check_user_edit_permission(current_user, user_id, current_user.role)
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        deleted_link = await link_dao.delete_link_by_id(link_id)

        if deleted_link is None:
            raise HTTPException(
                status_code=404, detail=f"Link with id {link_id} doesn't exist"
            )

        return UserSocialMediaLinkRead.from_orm_obj(deleted_link)
