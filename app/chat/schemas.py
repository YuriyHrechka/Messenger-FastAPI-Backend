from datetime import datetime
from typing import Optional, List
from pydantic import field_validator, model_validator
from sqlmodel import SQLModel
from app.users.schemas import UserRead


class ChatRead(SQLModel):
    id: int
    title: Optional[str]
    is_group: bool
    users: List[UserRead]
    created_at: datetime


class ChatCreate(SQLModel):
    title: Optional[str] = None
    is_group: bool = False
    participant_ids: List[int]

    @model_validator(mode="after")
    def check_group_title(self):
        if self.is_group and not self.title:
            raise ValueError("Group chat must have a title")
        return self

    @field_validator("participant_ids")
    @classmethod
    def check_unique_participants(cls, ids):
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate participant IDs are not allowed")
        return ids


class MessageRead(SQLModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime


class MessageCreate(SQLModel):
    content: str
