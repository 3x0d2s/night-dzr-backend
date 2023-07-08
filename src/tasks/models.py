from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base
from src.database.association_tables import AT_GamesTasks


class Task(Base):
    __tablename__ = "Task"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    mystery_of_place: Mapped[str] = mapped_column(String, nullable=False)
    place: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship(lazy="raise", back_populates="tasks")
    games: Mapped[list["Game"]] = relationship(lazy="raise", secondary=AT_GamesTasks, back_populates="tasks")
