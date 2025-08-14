from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.user_profile.dao import UserDAO
from src.user_profile.dao import UserPhotoDAO
from src.user_profile.dao import UserSocialMediaLinkDAO
from src.user_profile.schemas import UserCreate
from src.user_profile.schemas import UserPhotoCreate
from src.user_profile.schemas import UserPhotoRead
from src.user_profile.schemas import UserPhotoUpdate
from src.user_profile.schemas import UserRead
from src.user_profile.schemas import UserSocialMediaLinkCreate
from src.user_profile.schemas import UserSocialMediaLinkRead
from src.user_profile.schemas import UserSocialMediaLinkUpdate
from src.user_profile.schemas import UserUpdate


async def _create_user(body: UserCreate, db_session: AsyncSession) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        try:
            user = await user_dao.create_user(
                email=body.email,
                name=body.name,
                surname=body.surname,
                date_of_birth=body.date_of_birth,
                bio=body.bio,
                gender=body.gender,
                country=body.country,
                city=body.city,
            )
            return UserRead.from_orm_obj(user)
        except ValueError as e:
            if "already exists" in str(e):
                raise HTTPException(
                    status_code=400, detail="User with this email already exists"
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


async def _update_user(body: UserUpdate, id: UUID, db_session: AsyncSession) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
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


async def _delete_user(id: UUID, db_session: AsyncSession) -> UserRead:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        deleted_user = await user_dao.delete_user_by_id(id)
        if deleted_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {id} doesn't exist"
            )
        return UserRead.from_orm_obj(deleted_user)


async def _create_photo(
    body: UserPhotoCreate, user_id: UUID, db_session: AsyncSession
) -> UserPhotoRead:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        photo = await photo_dao.create_photo(user_id=user_id, url=body.url)
        return UserPhotoRead.from_orm_obj(photo)


async def _get_all_photos_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserPhotoRead]:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        photos = await photo_dao.get_all_photos_by_user(user_id)
        if photos is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} doesn't have a photo"
            )
        return [UserPhotoRead.from_orm_obj(photo) for photo in photos]


async def _delete_photo_by_id(
    user_id: UUID, photo_id: int, db_session: AsyncSession
) -> UserPhotoRead:
    async with db_session.begin():
        photo_dao = UserPhotoDAO(db_session)
        deleted_photo = await photo_dao.delete_photo_by_id(photo_id)

        if deleted_photo is None:
            raise HTTPException(
                status_code=404, detail=f"Photo with id {photo_id} doesn't exist"
            )

        return UserPhotoRead.from_orm_obj(deleted_photo)


async def _update_photo_by_id(
    body: UserPhotoUpdate, user_id: UUID, photo_id: int, db_session: AsyncSession
) -> UserPhotoRead:
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
    body: UserSocialMediaLinkCreate, user_id: UUID, db_session: AsyncSession
) -> UserSocialMediaLinkRead:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        link = await link_dao.create_link(user_id=user_id, link=body.link, name=body.name)
        return UserSocialMediaLinkRead.from_orm_obj(link)


async def _get_all_links_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[UserSocialMediaLinkRead]:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        links = await link_dao.get_all_links_by_user(user_id)
        return [UserSocialMediaLinkRead.from_orm_obj(link) for link in links]


async def _update_link_by_id(
    body: UserSocialMediaLinkUpdate, user_id: UUID, link_id: int, db_session: AsyncSession
) -> UserSocialMediaLinkRead:
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
    user_id: UUID, link_id: int, db_session: AsyncSession
) -> UserSocialMediaLinkRead:
    async with db_session.begin():
        link_dao = UserSocialMediaLinkDAO(db_session)
        deleted_link = await link_dao.delete_link_by_id(link_id)

        if deleted_link is None:
            raise HTTPException(
                status_code=404, detail=f"Link with id {link_id} doesn't exist"
            )

        return UserSocialMediaLinkRead.from_orm_obj(deleted_link)
