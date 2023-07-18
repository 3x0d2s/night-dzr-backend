from typing import Annotated
from fastapi import APIRouter, WebSocket, Depends, status, \
    WebSocketException, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from src.database.db import get_db_session
from src.config import config
from src.auth.models import User as UserModel
from src.chat.crud import ChatCrud
from src.websockets.ws_manager import Connection, WSConnectionManager

router = APIRouter()
ws_chat_manager = WSConnectionManager()
ws_events_manager = WSConnectionManager()


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
    connection = Connection(user_id=user.id, websocket=websocket)
    await ws_chat_manager.connect(chat.id, connection)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_chat_manager.disconnect(chat.id, connection)


@router.websocket("/ws/events")
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
    connection = Connection(user_id=user.id, websocket=websocket)
    await ws_events_manager.connect(chat.id, connection)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_events_manager.disconnect(chat.id, connection)
