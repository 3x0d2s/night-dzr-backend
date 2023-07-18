import json
from fastapi import WebSocket
from src.chat.shemas import MessageRead
from dataclasses import dataclass


@dataclass
class Connection:
    user_id: int
    websocket: WebSocket


class WSConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[Connection]] = {}

    async def connect(self, chat_id: int, conn: Connection):
        if chat_id not in self.active_connections.keys():
            self.active_connections[chat_id] = [conn]
        else:
            self.active_connections[chat_id].append(conn)
        await conn.websocket.send_text("Connected")

    def disconnect(self, chat_id: int, conn: Connection):
        self.active_connections[chat_id].remove(conn)

    async def send_message(self, message: MessageRead):
        for chat_member_conn in self.active_connections[message.chat_id]:
            if chat_member_conn.user_id != message.user_id:
                await chat_member_conn.websocket.send_text(json.dumps(message.dict(), indent=4, sort_keys=True))
