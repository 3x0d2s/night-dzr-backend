from fastapi import WebSocket
from src.chat.shemas import MessageRead


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket):
        if chat_id not in self.active_connections.keys():
            self.active_connections[chat_id] = [websocket]
        else:
            self.active_connections[chat_id].append(websocket)
        await websocket.send_text("Connected")

    def disconnect(self, chat_id: int, websocket: WebSocket):
        self.active_connections[chat_id].remove(websocket)

    async def send_message(self, message: MessageRead):
        for chat_member_ws in self.active_connections[message.chat_id]:
            await chat_member_ws.send_json(message.dict(exclude={"date"}))
