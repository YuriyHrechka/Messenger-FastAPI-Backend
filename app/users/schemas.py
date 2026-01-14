from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


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
    username: str = Field(unique=True, index=True)
    avatar_url: Optional[str] = None
