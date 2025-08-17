from typing import List
from uuid import UUID

from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dao import RefreshTokenDAO
from src.auth.schemas import (
    LoginRequest,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
    TokenRevokeRequest,
)
from src.auth.utils import create_access_token, get_password_hash, verify_password
from src.config import ALGORITHM, SECRET_KEY
from src.user_profile.dao import UserDAO


async def _create_tokens_by_user(
    user_id: UUID, user_role: str, db_session: AsyncSession
) -> TokenResponse:
    access_token = create_access_token(payload={"sub": str(user_id), "role": user_role})
    refresh_dao = RefreshTokenDAO(db_session)
    refresh_token = await refresh_dao.create_refresh_token_by_user(user_id=user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token.token)


async def _login_user(body: LoginRequest, db_session: AsyncSession) -> TokenResponse:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        user = await user_dao.get_user_by_email(email=body.email)

        if user is None or not verify_password(body.password, user.hash_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        return await _create_tokens_by_user(user.id, user.role, db_session)


async def _create_user(body: RegisterRequest, db_session: AsyncSession) -> TokenResponse:
    async with db_session.begin():
        user_dao = UserDAO(db_session)
        try:
            new_user = await user_dao.create_user(
                email=body.email,
                hash_password=get_password_hash(body.password),
                name=body.name,
                surname=body.surname,
                date_of_birth=body.date_of_birth,
                bio=body.bio,
                gender=body.gender,
                country=body.country,
                city=body.city,
            )

            return await _create_tokens_by_user(new_user.id, "user", db_session)

        except ValueError as e:
            if "already exists" in str(e):
                raise HTTPException(
                    status_code=400, detail="User with this email already exists"
                )


async def _update_access_token(
    plain_refresh_token: str, db_session: AsyncSession
) -> TokenResponse:
    async with db_session.begin():
        refresh_dao = RefreshTokenDAO(db_session)
        stored_refresh_token = await refresh_dao.get_refresh_token(plain_refresh_token)

        if not stored_refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token not found")

        if not stored_refresh_token.active:
            raise HTTPException(status_code=401, detail="Refresh token is not active")

        try:
            payload = jwt.decode(plain_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = UUID(payload.get("sub"))

        new_refresh_token = await refresh_dao.create_refresh_token_by_user(user_id)
        await refresh_dao.revoke_refresh_token(plain_refresh_token)
        access_token = create_access_token(payload={"sub": str(user_id)})

        return TokenResponse(
            access_token=access_token, refresh_token=new_refresh_token.token
        )


async def _revoke_refresh_token(
    body: TokenRevokeRequest, db_session: AsyncSession
) -> RefreshTokenResponse:
    async with db_session.begin():
        refresh_dao = RefreshTokenDAO(db_session)
        stored_refresh_token = await refresh_dao.get_refresh_token(body.refresh_token)

        if not stored_refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token not found")

        if not stored_refresh_token.active:
            raise HTTPException(
                status_code=401, detail="Refresh token is already revoked"
            )

        try:
            jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        await refresh_dao.revoke_refresh_token(body.refresh_token)

        return RefreshTokenResponse(refresh_token=body.refresh_token, active=False)


async def _revoke_all_refresh_tokens_by_user(
    user_id: UUID, db_session: AsyncSession
) -> List[RefreshTokenResponse]:
    async with db_session.begin():
        refresh_dao = RefreshTokenDAO(db_session)
        revoked_tokens = await refresh_dao.revoke_all_refresh_tokens_by_user(user_id)
        return [
            RefreshTokenResponse(refresh_token=revoked_token.token, active=False)
            for revoked_token in revoked_tokens
        ]


async def login_user(body: LoginRequest, db_session: AsyncSession) -> TokenResponse:
    return await _login_user(body, db_session)


async def register_user(body: RegisterRequest, db_session: AsyncSession) -> TokenResponse:
    return await _create_user(body, db_session)


async def update_access_token(
    plain_refresh_token: str, db_session: AsyncSession
) -> TokenResponse:
    return await _update_access_token(plain_refresh_token, db_session)


async def revoke_refresh_token(
    body: TokenRevokeRequest, db_session: AsyncSession
) -> RefreshTokenResponse:
    return await _revoke_refresh_token(body, db_session)
