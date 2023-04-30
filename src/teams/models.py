from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.auth.models import User

association_table = Table(
    "TeamUsers",
    Base.metadata,
    Column("team_id", ForeignKey("Team.id")),
    Column("user_id", ForeignKey("User.id")),
)


class Team(Base):
    __tablename__ = "Team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_games: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    users: Mapped[list[User]] = relationship(lazy="raise", secondary=association_table)
