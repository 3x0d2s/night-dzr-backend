from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.db import Base
from src.database.association_tables import AT_TeamUsers


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "User"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    surname: Mapped[str] = mapped_column(String(length=32), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(length=32), nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(length=11), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_games: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    team: Mapped["Team"] = relationship(lazy="raise", secondary=AT_TeamUsers, back_populates="users")
    tasks: Mapped[list["Task"]] = relationship(lazy="raise", back_populates="user")
    games: Mapped[list["Game"]] = relationship(lazy="raise", back_populates="user")
