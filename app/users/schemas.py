from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class UserBase(SQLModel):
    """Shared properties for User models.

    This class serves as the base for the User table and Pydantic
    schemas (e.g., UserCreate, UserRead).

    Attributes:
        email (str): The user's email address. Marked as unique in the table model.
        username (str): The user's display name. Marked as unique in the table model.
        avatar_url (Optional[str]): URL string to the user's profile image.
            Defaults to None.
    """

    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, max_length=12)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    created_at: datetime
    last_online: datetime
