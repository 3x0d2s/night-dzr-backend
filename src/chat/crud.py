from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.auth.models import User
from src.chat.models import Chat, Message


class ChatCrud:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_message(self, message_data, user_id: int):
        """ Создаёт запись сообщения в БД.  """
        db_msg = Message(**message_data.dict(), date=datetime.utcnow(), user_id=user_id)
        self.db.add(db_msg)
        return db_msg

    async def get_user_data(self, user_id: int) -> User:
        """ Возвращает данные пользователя вместе с данными его команды. """
        query = select(User).filter(User.id == user_id).options(selectinload(User.team))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_team_active_chat(self, team_id: int) -> Chat:
        """ Возвращает активный чат для переданной команды. """
        query = select(Chat).filter(and_(Chat.team_id == team_id, Chat.is_active.is_(True)))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_active_chats(self) -> list[Chat]:
        """ Возвращает все активные чаты. """
        query = select(Chat).filter(Chat.is_active.is_(True)).options(selectinload(Chat.team))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance: object):
        await self.db.refresh(instance)
