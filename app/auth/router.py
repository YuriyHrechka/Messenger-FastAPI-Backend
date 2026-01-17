from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.deps import UserServiceDep
from app.core.settings import settings
from app.users.models import User
from app.core.deps import SessionDep
from .schemas import TokenRefresh


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
    user_id_str = verify_token(token_data.refresh_token, required_type="refresh")

    user = await session.get(User, int(user_id_str))
    if not user or not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
