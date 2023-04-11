from sqlalchemy import Boolean, Column, Integer, String, BigInteger, null
from app.sql.database import Base


class User(Base):
    __tablename__ = "users"
    #
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(length=32), nullable=False)
    surname = Column(String(length=32), nullable=False)
    patronymic = Column(String(length=32), nullable=False)
    email = Column(String(length=128), nullable=False)
    phone_number = Column(String(length=11), nullable=False)
    hashed_password = Column(String, nullable=False)
    games_played = Column(Integer, nullable=False)
    win_games = Column(Integer, nullable=False)
    is_organizer = Column(Boolean, nullable=False, default=False)
    team_id = Column(BigInteger, default=null)
