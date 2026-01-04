from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


def get_utc_now():
    return datetime.now(timezone.utc)


class ChatParticipant(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    chat_id: int = Field(foreign_key="chat.id", primary_key=True)
    joined_at: datetime = Field(default_factory=get_utc_now)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    chats: List["Chat"] = Relationship(
        back_populates="users", link_model=ChatParticipant
    )
    messages: List["Message"] = Relationship(back_populates="sender")
    last_online: datetime = Field(default_factory=get_utc_now)


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    is_group: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_utc_now)

    users: List[User] = Relationship(back_populates="chats", link_model=ChatParticipant)
    messages: List["Message"] = Relationship(back_populates="chat")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=get_utc_now)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    chat: Chat = Relationship(back_populates="messages")
    sender: User = Relationship(back_populates="messages")
