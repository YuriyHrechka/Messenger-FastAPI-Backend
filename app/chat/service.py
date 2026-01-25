from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import col, desc, select
from typing import Optional, Sequence

from .models import Chat, ChatParticipant, Message
from .schemas import ChatCreate, ChatUpdate, MessageCreate
from app.users.models import User


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_chat(self, chat_data: ChatCreate, current_user_id: int):
        await self._validate_if_users_exist(chat_data)

        participant_ids = set(chat_data.participant_ids)
        participant_ids.discard(current_user_id)

        if not chat_data.is_group and len(participant_ids) == 1:
            target_user_id = list(participant_ids)[0]
            existing_chat = await self._check_existing_direct_chat(current_user_id, target_user_id)
            if existing_chat:
                return existing_chat

        new_chat = Chat(title=chat_data.title, is_group=chat_data.is_group)
        self.session.add(new_chat)

        await self.session.flush()
        await self.session.refresh(new_chat)

        final_participant_ids = participant_ids | {current_user_id}

        participants = [
            ChatParticipant(user_id=uid, chat_id=new_chat.id) for uid in final_participant_ids  # type: ignore
        ]
        self.session.add_all(participants)

        await self.session.commit()
        return await self._get_chat_with_users(new_chat.id)  # type: ignore

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

    async def get_chat_by_id(self, chat_id: int, user_id: int) -> Chat:
        statement = select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.users))  # type: ignore

        result = await self.session.exec(statement)
        chat = result.first()

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        await self._validate_participation(chat_id, user_id)

        return chat

    async def update_chat(self, chat_id: int, chat_data: ChatUpdate, user_id: int) -> Chat:
        await self._validate_participation(chat_id, user_id)

        db_chat = await self._get_chat_with_users(chat_id)

        if not db_chat.is_group and chat_data.title:
            raise HTTPException(status_code=400, detail="Cannot update title of a direct chat")

        if chat_data.title:
            db_chat.title = chat_data.title

        self.session.add(db_chat)
        await self.session.commit()
        await self.session.refresh(db_chat)
        return db_chat

    async def remove_participant(self, chat_id: int, user_id: int) -> ChatParticipant:
        participant = await self.session.get(ChatParticipant, (user_id, chat_id))

        if not participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant of this chat")

        await self.session.delete(participant)
        await self.session.commit()

        return participant

    async def send_message(self, message_data: MessageCreate, chat_id: int, user_id: int) -> Message:
        await self._validate_participation(chat_id, user_id)

        db_message = Message(content=message_data.content, chat_id=chat_id, sender_id=user_id)

        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return db_message

    async def get_chat_messages(self, chat_id: int, user_id: int, limit: int, offset: int) -> Sequence[Message]:
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

    async def get_message_by_id(self, message_id: int, chat_id: int, user_id: int) -> Message:
        await self._validate_participation(chat_id, user_id)

        statement = select(Message).where(Message.id == message_id, Message.chat_id == chat_id)
        result = await self.session.exec(statement)
        message = result.first()

        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found in this chat")

        return message

    async def delete_message(self, message_id: int, chat_id: int, user_id: int):
        message = await self.get_message_by_id(message_id, chat_id, user_id)

        if message.sender_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own messages")

        await self.session.delete(message)
        await self.session.commit()

    async def _check_existing_direct_chat(self, user1_id: int, user2_id: int) -> Optional[Chat]:
        statement = (
            select(Chat)
            .join(ChatParticipant)
            .where(Chat.is_group == False)
            .where(ChatParticipant.user_id == user1_id)
            .intersect(
                select(Chat)
                .join(ChatParticipant)
                .where(Chat.is_group == False)
                .where(ChatParticipant.user_id == user2_id)
            )
        )

        result = await self.session.execute(statement)
        chat = result.scalars().first()

        if chat and chat.id:
            return await self._get_chat_with_users(chat.id)

        return None

    async def _get_chat_with_users(self, chat_id: int) -> Chat:
        statement = select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.users))  # type: ignore
        result = await self.session.exec(statement)
        chat = result.first()

        if chat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No chat found with ID {chat_id}")

        return chat

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
