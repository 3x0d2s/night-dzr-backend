from typing import Annotated
from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db_session
from src.auth.auth import current_user, current_seperuser
from src.auth.schemas import UserRead
from src.chat.crud import ChatCrud
from src.websockets.router import ws_chat_manager
from src.chat.shemas import MessageCreate, MessageRead, ChatRead

router = APIRouter()


@router.post("/message/send",
             summary="Send message",
             response_model=MessageRead,
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
             })
async def send_message(message: Annotated[MessageCreate, Body()],
                       db: Annotated[AsyncSession, Depends(get_db_session)],
                       user_request_data: Annotated[UserRead, Depends(current_user)]):
    chat_crud = ChatCrud(db)
    db_msg = await chat_crud.create_message(message, user_id=user_request_data.id)
    await chat_crud.commit()
    await chat_crud.refresh(db_msg)

    msg = MessageRead(**db_msg.as_dict(exclude=["date"]),
                      date=db_msg.date.timestamp()
                      )
    await ws_chat_manager.send_message(msg)
    return msg


@router.get("/chats/iter_active",
            summary="Iter active chats",
            response_model=list[ChatRead],
            responses={
                status.HTTP_201_CREATED: {
                    "description": "Successful Response"},
            })
async def iter_active_chats(db: Annotated[AsyncSession, Depends(get_db_session)],
                            user_request_data: Annotated[UserRead, Depends(current_seperuser)]):
    chat_crud = ChatCrud(db)
    chats = await chat_crud.get_active_chats()
    result = []
    for chat in chats:
        result.append(ChatRead(**chat.as_dict(), team_name=chat.team.name))
    return result
