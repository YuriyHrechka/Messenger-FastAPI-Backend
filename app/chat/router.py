from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from app.core.deps import CurrentUser, ChatServiceDep
from app.chat.schemas import ChatCreate, ChatRead, ChatUpdate, MessageCreate, MessageRead

router = APIRouter()


@router.post("/", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(chat_data: ChatCreate, current_user: CurrentUser, service: ChatServiceDep):
    return await service.create_chat(chat_data, current_user.id)  # type: ignore


@router.get("/", response_model=List[ChatRead])
async def get_my_chats(current_user: CurrentUser, service: ChatServiceDep):
    return await service.get_user_chats(current_user.id)  # type: ignore


@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat_details(chat_id: int, current_user: CurrentUser, service: ChatServiceDep):
    return await service.get_chat_by_id(chat_id, current_user.id)  # type: ignore


@router.patch("/{chat_id}", response_model=ChatRead)
async def update_chat(chat_id: int, chat_update: ChatUpdate, current_user: CurrentUser, service: ChatServiceDep):
    return await service.update_chat(chat_id, chat_update, current_user.id)  # type: ignore


@router.delete("/{chat_id}/participants/me", status_code=status.HTTP_204_NO_CONTENT)
async def leave_chat(chat_id: int, current_user: CurrentUser, service: ChatServiceDep):
    await service.remove_participant(chat_id, current_user.id)  # type: ignore


@router.get("/{chat_id}/messages", response_model=List[MessageRead])
async def get_chat_history(
    chat_id: int,
    current_user: CurrentUser,
    service: ChatServiceDep,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await service.get_chat_messages(chat_id, current_user.id, limit, offset)  # type: ignore


@router.post("/{chat_id}/messages", response_model=MessageRead)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: CurrentUser,
    service: ChatServiceDep,
):
    return await service.send_message(message_data, chat_id, current_user.id)  # type: ignore


@router.delete("/{chat_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(chat_id: int, message_id: int, current_user: CurrentUser, service: ChatServiceDep):
    await service.delete_message(message_id, chat_id, current_user.id)  # type: ignore
