from sqlalchemy import Boolean, Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.auth.models import User


class Team(Base):
    __tablename__ = "Team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_games: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    user_ids: Mapped[list[User]] = relationship()
