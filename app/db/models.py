from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


def get_utc_now():
    """Gets the current timezone-aware datetime in UTC.

    Returns:
        datetime: The current time in UTC.
    """
    return datetime.now(timezone.utc)


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
    joined_at: datetime = Field(default_factory=get_utc_now)


class User(SQLModel, table=True):
    """Represents a registered user in the application.

    Attributes:
        id (Optional[int]): The unique identifier for the user.
        email (str): The user's email address. Must be unique.
        username (str): The user's display name. Must be unique.
        hashed_password (str): The hashed version of the user's password for security.
        avatar_url (Optional[str]): URL string to the user's profile image. Defaults to None.
        created_at (datetime): Timestamp when the account was created.
            Defaults to the current UTC time.
        last_online (datetime): Timestamp of the user's last known activity.
            Defaults to the current UTC time.
        chats (List[Chat]): A list of Chat objects this user is a participant of.
        messages (List[Message]): A list of Message objects sent by this user.
    """

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
    created_at: datetime = Field(default_factory=get_utc_now)

    users: List[User] = Relationship(back_populates="chats", link_model=ChatParticipant)
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
    created_at: datetime = Field(default_factory=get_utc_now)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    chat: Chat = Relationship(back_populates="messages")
    sender: User = Relationship(back_populates="messages")
