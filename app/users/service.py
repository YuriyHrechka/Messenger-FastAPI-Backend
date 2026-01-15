from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.users.models import User
from app.users.schemas import UserCreate
from app.core.security import get_password_hash


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = await self.session.exec(statement)
        return result.first()

    async def user_exists(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def create_user(self, user_in: UserCreate) -> User:
        user_dict = user_in.model_dump(exclude={"password"})

        new_user = User(**user_dict)
        new_user.hashed_password = get_password_hash(user_in.password)

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
