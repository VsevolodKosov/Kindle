import uuid

import pytest


@pytest.mark.asyncio
async def test_check_user_edit_permission_roles(client, user_with_token):
    from src.user_profile.schemas import UserRead
    from src.user_profile.utils import check_user_edit_permission

    current = user_with_token["user_data"]
    user_id = (
        uuid.UUID(current["user_id"])
        if isinstance(current["user_id"], str)
        else current["user_id"]
    )
    as_read = UserRead(
        user_id=user_id,
        email=current["email"],
        name=current["name"],
        surname=current["surname"],
        date_of_birth=current["date_of_birth"],
        bio=current["bio"],
        gender=current["gender"],
        country=current["country"],
        city=current["city"],
        role="user",
    )

    check_user_edit_permission(as_read, user_id)
    with pytest.raises(Exception):
        check_user_edit_permission(as_read, uuid.uuid4())

    as_read.role = "moderator"
    with pytest.raises(Exception):
        check_user_edit_permission(as_read, uuid.uuid4())

    as_read.role = "admin"
    check_user_edit_permission(as_read, uuid.uuid4())


@pytest.mark.asyncio
async def test_check_user_delete_permission_roles(client, user_with_token):
    from src.user_profile.schemas import UserRead
    from src.user_profile.utils import check_user_delete_permission

    current = user_with_token["user_data"]
    user_id = (
        uuid.UUID(current["user_id"])
        if isinstance(current["user_id"], str)
        else current["user_id"]
    )
    as_read = UserRead(
        user_id=user_id,
        email=current["email"],
        name=current["name"],
        surname=current["surname"],
        date_of_birth=current["date_of_birth"],
        bio=current["bio"],
        gender=current["gender"],
        country=current["country"],
        city=current["city"],
        role="user",
    )

    check_user_delete_permission(as_read, user_id, "user")
    with pytest.raises(Exception):
        check_user_delete_permission(as_read, uuid.uuid4(), "user")

    as_read.role = "moderator"
    check_user_delete_permission(as_read, uuid.uuid4(), "user")
    for role in ["moderator", "admin"]:
        with pytest.raises(Exception):
            check_user_delete_permission(as_read, uuid.uuid4(), role)

    as_read.role = "admin"
    for role in ["user", "moderator", "admin"]:
        check_user_delete_permission(as_read, uuid.uuid4(), role)
