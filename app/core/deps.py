from typing import Annotated
from fastapi import Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.core.settings import settings
from app.db.session import get_session
from app.users.service import UserService
from app.users.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: TokenDep,
    service: UserServiceDep,
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(token_data)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
