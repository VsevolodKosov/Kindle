from uuid import UUID

from fastapi import HTTPException, status

from src.user_profile.schemas import UserRead


def check_user_ownership(current_user: UserRead, target_user_id: UUID) -> None:
    if current_user.user_id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own account",
        )


def check_user_edit_permission(current_user: UserRead, target_user_id: UUID):
    if current_user.role == "user":
        if current_user.user_id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only modify their own profile",
            )

    elif current_user.role == "moderator":
        if current_user.user_id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderators cannot modify other user profiles",
            )

    elif current_user.role == "admin":
        return

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown role")


def check_user_delete_permission(
    current_user: UserRead, target_user_id: UUID, target_role: str
):
    if current_user.role == "user":
        if current_user.user_id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only delete their own profile",
            )

    elif current_user.role == "moderator":
        if target_role != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderators can only delete users",
            )

    elif current_user.role == "admin":
        return

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown role")
