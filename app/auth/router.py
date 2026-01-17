from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.deps import AuthServiceDep, TokenDep, UserServiceDep
from app.users.models import User
from app.core.deps import SessionDep
from .schemas import TokenRefresh

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserServiceDep,
):
    user = await user_service.get_by_email(form_data.username)

    if (
        not user
        or not user.id
        or not verify_password(form_data.password, user.hashed_password)
    ):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_access_token(
    token_data: TokenRefresh,
    session: SessionDep,
):
    try:
        payload = verify_token(token_data.refresh_token, required_type="refresh")
        user_id_str = payload.get("sub")

        user = await session.get(User, int(user_id_str))  # type: ignore
        if not user or not user.id:
            logger.warning(f"Token refresh failed: User ID {user_id_str} not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
        raise e


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: TokenDep,
    auth_service: AuthServiceDep,
):

    payload = verify_token(token, required_type="access")
    jti = payload.get("jti")
    exp_timestamp = payload.get("exp")

    if jti and exp_timestamp:
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp_timestamp - now)

        if ttl > 0:
            await auth_service.revoke_token(jti, ttl)

    return {"message": "Logged out successfully"}
