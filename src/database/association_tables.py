from sqlalchemy import ForeignKey, Table, Column
from src.database.db import Base


AT_TeamUsers = Table(
    "TeamUsers",
    Base.metadata,
    Column("team_id", ForeignKey("Team.id")),
    Column("user_id", ForeignKey("User.id")),
)
