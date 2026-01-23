from fastapi import HTTPException, status
from sqlalchemy import ScalarResult
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from app.chat.models import Chat, ChatParticipant, Message
from app.chat.schemas import ChatCreate, MessageCreate
from app.users.models import User
from typing import List, Sequence


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_chat(self, chat_data: ChatCreate, current_user_id: int):
        new_chat = Chat(title=chat_data.title, is_group=chat_data.is_group)

        self.session.add(new_chat)
        await self.session.commit()
        await self.session.refresh(new_chat)

        admin_participant = ChatParticipant(
            user_id=current_user_id, chat_id=new_chat.id  # type: ignore
        )
        self.session.add(admin_participant)

        unique_ids = set(chat_data.participant_ids)
        if current_user_id in unique_ids:
            unique_ids.remove(current_user_id)

        for user_id in unique_ids:
            participant = ChatParticipant(user_id=user_id, chat_id=new_chat.id)  # type: ignore
            self.session.add(participant)

        await self.session.commit()
        await self.session.refresh(new_chat)
        return new_chat

    async def get_user_chats(self, user_id: int) -> Sequence[Chat]:
        statement = (
            select(Chat)
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
