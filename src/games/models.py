from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base
from src.database.association_tables import AT_GamesTasks, AT_GamesTeams


class Game(Base):
    __tablename__ = "Game"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    legend: Mapped[str] = mapped_column(String, nullable=False)
    datetime_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    datetime_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user: Mapped["User"] = relationship(lazy="raise", back_populates="games")
    tasks: Mapped[list["Task"]] = relationship(lazy="raise", secondary=AT_GamesTasks, back_populates="games")
    teams: Mapped[list["Team"]] = relationship(lazy="raise", secondary=AT_GamesTeams, back_populates="games")
