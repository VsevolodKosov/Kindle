from typing import List
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.schemas import (
    LoginRequest,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
    TokenRevokeRequest,
)
from src.auth.services import (
    _create_user,
    _login_user,
    _revoke_all_refresh_tokens_by_user,
    _revoke_refresh_token,
    _update_access_token,
)
from src.config import (
    COOKIE_ACCESS_TOKEN_MAX_AGE,
    COOKIE_HTTPONLY,
    COOKIE_REFRESH_TOKEN_MAX_AGE,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
)
from src.database import get_async_db_session
from src.user_profile.schemas import UserRead
from src.user_profile.service import (
    _demote_moderator,
    _get_all_users,
    _get_users_by_role,
    _promote_user,
)

auth_router = APIRouter()
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    tokens = await _login_user(body, db_session)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_ACCESS_TOKEN_MAX_AGE,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_REFRESH_TOKEN_MAX_AGE,
    )

    return tokens


@auth_router.post("/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    response: Response,
    db_session: AsyncSession = Depends(get_async_db_session),
):
    tokens = await _create_user(body, db_session)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_ACCESS_TOKEN_MAX_AGE,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_REFRESH_TOKEN_MAX_AGE,
    )

    return tokens


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_token: str = Cookie(None),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found in cookies")

    tokens = await _update_access_token(
        plain_refresh_token=refresh_token, db_session=db_session
    )

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_ACCESS_TOKEN_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=COOKIE_REFRESH_TOKEN_MAX_AGE,
    )

    return tokens


@auth_router.post("/revoke", response_model=RefreshTokenResponse)
async def revoke_refresh_token(
    refresh_token: str = Cookie(None),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found in cookies")

    return await _revoke_refresh_token(
        TokenRevokeRequest(refresh_token=refresh_token), db_session
    )


@auth_router.post("/logout", response_model=List[RefreshTokenResponse])
async def logout(
    response: Response,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    revoked_tokens = await _revoke_all_refresh_tokens_by_user(
        current_user.user_id, db_session
    )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return revoked_tokens


@auth_router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: UserRead = Depends(get_current_user),
):
    return current_user


@admin_router.get("/users", response_model=List[UserRead])
async def get_all_users(
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _get_all_users(current_user, db_session)


@admin_router.get("/users/moderators", response_model=List[UserRead])
async def get_moderators(
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _get_users_by_role("moderator", current_user, db_session)


@admin_router.get("/users/admins", response_model=List[UserRead])
async def get_admins(
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _get_users_by_role("admin", current_user, db_session)


@admin_router.post("/users/{user_id}/promote", response_model=UserRead)
async def promote_to_moderator(
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _promote_user(user_id, current_user, db_session)


@admin_router.post("/users/{user_id}/demote", response_model=UserRead)
async def demote_moderator(
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
):
    return await _demote_moderator(user_id, current_user, db_session)
