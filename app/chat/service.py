from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import col, desc, select
from typing import List, Sequence

from .models import Chat, ChatParticipant, Message
from .schemas import ChatCreate, MessageCreate
from app.users.models import User


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_chat(self, chat_data: ChatCreate, current_user_id: int):   
        await self._validate_if_users_exist(chat_data)
        
        new_chat = Chat(title=chat_data.title, is_group=chat_data.is_group)
        self.session.add(new_chat)
        await self.session.commit()
        await self.session.refresh(new_chat)

        all_participant_ids = set(chat_data.participant_ids)
        all_participant_ids.add(current_user_id)

        participants = [
            ChatParticipant(user_id=uid, chat_id=new_chat.id)  # type: ignore
            for uid in all_participant_ids
        ]
        self.session.add_all(participants)
        await self.session.commit()

        statement = (
            select(Chat)
            .where(Chat.id == new_chat.id)
            .options(selectinload(Chat.users))  # type: ignore
        )
        result = await self.session.exec(statement)
        
        return result.one()

    async def get_user_chats(self, user_id: int) -> Sequence[Chat]:
        statement = (
            select(Chat)
            .options(selectinload(Chat.users))  # type: ignore
            .join(ChatParticipant)
            .where(ChatParticipant.user_id == user_id)
            .order_by(desc(Chat.created_at))
        )

        result = await self.session.exec(statement)
        return result.all()

    async def send_message(
        self, message_data: MessageCreate, chat_id: int, user_id: int
    ) -> Message:
        await self._validate_participation(chat_id, user_id)

        db_message = Message(
            content=message_data.content, chat_id=chat_id, sender_id=user_id
        )

        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return db_message

    async def get_chat_messages(
        self, chat_id: int, user_id: int, limit: int, offset: int
    ) -> Sequence[Message]:
        await self._validate_participation(chat_id, user_id)

        statement = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.exec(statement)
        return result.all()

    async def _validate_participation(self, chat_id: int, user_id: int):
        chat_participant = await self.session.get(ChatParticipant, (user_id, chat_id))

        if chat_participant is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not chat participant",
            )

    async def _validate_if_users_exist(self, chat_data: ChatCreate):
        statement = select(User.id).where(col(User.id).in_(chat_data.participant_ids))

        result = await self.session.exec(statement)
        found_ids = result.all()

        if len(found_ids) != len(set(chat_data.participant_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more participants do not exist",
            )
