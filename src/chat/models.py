from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base


class Chat(Base):
    __tablename__ = "Chat"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("Game.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("Team.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    team: Mapped["Team"] = relationship(lazy="raise")

    def as_dict(self, exclude: list[str] | None = None):
        if exclude is None:
            exclude = []
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}


class Message(Base):
    __tablename__ = "Message"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("Chat.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    reply_to: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)
    user: Mapped["User"] = relationship(lazy="raise")

    def as_dict(self, exclude: list[str] | None = None):
        if exclude is None:
            exclude = []
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}
