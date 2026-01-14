from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Column, DateTime, SQLModel, Field, Relationship, text
from .schemas import UserBase
from app.chat.models import ChatParticipant, Chat, Message


class User(UserBase, table=True):
    """Represents a registered user in the application database.

    Inherits email, username, and avatar_url from UserBase.

    Attributes:
        id (Optional[int]): The unique identifier for the user.
        hashed_password (str): The hashed version of the user's password for security.
        created_at (datetime): Timestamp when the account was created.
            Defaults to the current UTC time.
        last_online (datetime): Timestamp of the user's last known activity.
            Defaults to the current UTC time.
        chats (List[Chat]): A list of Chat objects this user is a participant of.
        messages (List[Message]): A list of Message objects sent by this user.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        )
    )
    chats: List["Chat"] = Relationship(
        back_populates="users", link_model=ChatParticipant
    )
    messages: List["Message"] = Relationship(back_populates="sender")
    last_online: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        )
    )
