from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base
from src.database.association_tables import AT_TeamUsers, AT_GamesTeams


class Team(Base):
    __tablename__ = "Team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_games: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    users: Mapped[list["User"]] = relationship(lazy="raise", secondary=AT_TeamUsers, back_populates="team")
    games: Mapped[list["Game"]] = relationship(lazy="raise", secondary=AT_GamesTeams,
                                               back_populates="teams", order_by="Game.datetime_start")
