from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.auth.service import AuthService
from app.core.security import verify_token
from app.core.settings import settings
from app.db.session import get_session
from app.users.service import UserService
from app.users.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_session)]

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis


RedisDep = Annotated[Redis, Depends(get_redis_client)]


def get_auth_service(redis: RedisDep) -> AuthService:
    return AuthService(redis)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: TokenDep,
    service: UserServiceDep,
    auth_service: AuthServiceDep,
) -> User:

    payload = verify_token(token, required_type="access")

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if jti:
        if await auth_service.is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token contains no user identity",
        )

    user = await service.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
