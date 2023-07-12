from typing import Annotated
from fastapi import APIRouter, WebSocket, Depends, Path, Body, status, Query, WebSocketException, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from src.database.db import get_db_session
from src.auth.auth import current_user
from src.auth.schemas import UserRead
from src.chat.crud import ChatCrud
from src.config import config
from src.auth.models import User as UserModel
from src.chat.conn_manager import ConnectionManager
from src.chat.shemas import MessageCreate, MessageRead

router = APIRouter()
manager = ConnectionManager()


async def get_user(token: str, db: AsyncSession) -> UserModel:
    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, config.SECURITY_KEY.get_secret_value(),
                             algorithms=["HS256"], audience="fastapi-users:auth")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        chat_crud = ChatCrud(db)
        user: UserModel = await chat_crud.get_user_data(int(user_id))
        return user


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket,
                             db: Annotated[AsyncSession, Depends(get_db_session)]
                             ):
    await websocket.accept()
    token = await websocket.receive_text()

    user = await get_user(token, db)
    if user is None:
        await websocket.close(status.WS_1011_INTERNAL_ERROR, "authentication failed")
        return

    chat_crud = ChatCrud(db)
    chat = await chat_crud.get_team_active_chat(user.team.id)
    await manager.connect(chat.id, websocket)

    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(chat.id, websocket)


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
    db_msg = await chat_crud.create_message(message)
    await chat_crud.commit()
    await chat_crud.refresh(db_msg)

    msg = MessageRead(**db_msg.as_dict())
    await manager.send_message(msg)

    return msg

