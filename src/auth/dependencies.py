from uuid import UUID

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import ALGORITHM, SECRET_KEY
from src.database import get_async_db_session
from src.user_profile.dao import UserDAO
from src.user_profile.schemas import UserRead

security = HTTPBearer(auto_error=False)


async def get_current_user(
    access_token: str = Cookie(None),
    authorization: HTTPAuthorizationCredentials = Depends(security),
    db_session: AsyncSession = Depends(get_async_db_session),
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = access_token or (authorization.credentials if authorization else None)
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role", "user")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        async with db_session.begin():
            user_dao = UserDAO(db_session)
            user = await user_dao.get_user_by_id(UUID(user_id))

            if user is None:
                raise credentials_exception

            user_read = UserRead.from_orm_obj(user)
            user_read.role = user_role
            return user_read
    finally:
        await db_session.close()
