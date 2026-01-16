from fastapi import APIRouter, HTTPException, status
from .schemas import UserCreate, UserRead
from app.core.deps import CurrentUser, UserServiceDep


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, user_service: UserServiceDep):
    if await user_service.get_by_email(user_data.email):
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    if await user_service.get_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    return await user_service.create_user(user_data)


@router.get("/profile", response_model=UserRead)
async def read_user_profile(current_user: CurrentUser):
    return current_user
