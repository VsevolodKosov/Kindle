from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import RefreshToken
from src.auth.utils import create_refresh_token


class RefreshTokenDAO:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_refresh_token_by_user(self, user_id: UUID) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=create_refresh_token({"sub": str(user_id)}),
            active=True,
        )
        self.db_session.add(refresh_token)
        await self.db_session.flush()
        return refresh_token

    async def get_refresh_token(self, plain_token: str) -> Optional[RefreshToken]:
        db_query = select(RefreshToken).where(RefreshToken.token == plain_token)
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> Optional[RefreshToken]:
        db_query = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(active=False)
            .returning(RefreshToken)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalar_one_or_none()

    async def revoke_all_refresh_tokens_by_user(
        self, user_id: UUID
    ) -> List[RefreshToken]:
        db_query = (
            update(RefreshToken)
            .where(and_(RefreshToken.user_id == user_id, RefreshToken.active))
            .values(active=False)
            .returning(RefreshToken)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()

    async def delete_all_revoked_refresh_tokens_by_user(
        self, user_id: UUID
    ) -> List[RefreshToken]:
        db_query = (
            delete(RefreshToken)
            .where(and_(RefreshToken.user_id == user_id, ~RefreshToken.active))
            .returning(RefreshToken)
        )
        db_response = await self.db_session.execute(db_query)
        return db_response.scalars().all()
