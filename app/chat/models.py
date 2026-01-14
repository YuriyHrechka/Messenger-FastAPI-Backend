from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Column, DateTime, SQLModel, Field, Relationship, text

if TYPE_CHECKING:
    from users.models import User


class ChatParticipant(SQLModel, table=True):
    """Represents the many-to-many link between Users and Chats.

    This association model tracks which users belong to which chats and when
    they joined.

    Attributes:
        user_id (int): Foreign key referencing the User ID. Part of the composite primary key.
        chat_id (int): Foreign key referencing the Chat ID. Part of the composite primary key.
        joined_at (datetime): Timestamp indicating when the user joined the chat.
            Defaults to the current UTC time.
    """

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    chat_id: int = Field(foreign_key="chat.id", primary_key=True)
    joined_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        )
    )


class Chat(SQLModel, table=True):
    """Represents a conversation room (either direct or group).

    Attributes:
        id (Optional[int]): The unique identifier for the chat.
        title (Optional[str]): The name of the chat (typically used for group chats).
            Defaults to None.
        is_group (bool): Flag indicating if the chat is a group conversation.
            Defaults to False.
        created_at (datetime): Timestamp when the chat was initialized.
            Defaults to the current UTC time.
        users (List[User]): A list of User objects participating in this chat.
        messages (List[Message]): A list of Message objects belonging to this chat.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    is_group: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        )
    )

    users: List["User"] = Relationship(
        back_populates="chats", link_model=ChatParticipant
    )
    messages: List["Message"] = Relationship(back_populates="chat")


class Message(SQLModel, table=True):
    """Represents a single text message sent within a chat.

    Attributes:
        id (Optional[int]): The unique identifier for the message.
        content (str): The text content of the message.
        created_at (datetime): Timestamp when the message was sent.
            Defaults to the current UTC time.
        chat_id (int): Foreign key referencing the Chat this message belongs to.
        sender_id (int): Foreign key referencing the User who sent this message.
        chat (Chat): The Chat object associated with this message.
        sender (User): The User object associated with this message.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            nullable=False,
        )
    )
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    chat: Chat = Relationship(back_populates="messages")
    sender: "User" = Relationship(back_populates="messages")
