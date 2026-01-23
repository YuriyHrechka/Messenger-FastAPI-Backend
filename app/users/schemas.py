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
    """Properties required to register a new user.

    This model inherits from UserBase and adds sensitive information
    required only during account creation.

    Attributes:
        password (str): The raw password input by the user. Must be at least
            8 characters long. Note: This should be hashed before storage.
    """

    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Public properties returned to the client.

    This model is used for data serialization (responses). It includes
    database-generated fields (like ID and timestamps) but excludes
    sensitive data like the password.

    Attributes:
        id (int): The unique database primary key for the user.
        created_at (datetime): The UTC timestamp of when the account was created.
        last_online (datetime): The UTC timestamp of the user's last activity.
    """

    id: int
    created_at: datetime
    last_online: datetime
