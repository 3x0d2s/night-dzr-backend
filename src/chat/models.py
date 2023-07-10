import enum
from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base


class ContentTypes(enum.Enum):
    text = 1


class Message(Base):
    __tablename__ = "Message"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("Team.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("Game.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_type: Mapped[ContentTypes] = mapped_column(Enum(ContentTypes).values_callable, nullable=False)
    text: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    media: Mapped[str] = mapped_column(String(128), nullable=True, default=None)
    is_reply: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reply_to: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)
    user: Mapped["User"] = relationship(lazy="raise")
