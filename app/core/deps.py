from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_token
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

    user_id = verify_token(token, required_type="access")

    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
