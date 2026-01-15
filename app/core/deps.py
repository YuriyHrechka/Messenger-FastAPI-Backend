from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.core.settings import settings
from app.db.session import get_session
from app.users.service import UserService

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
