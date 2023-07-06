from sqlalchemy import ForeignKey, Table, Column
from src.database.db import Base


AT_TeamUsers = Table(
    "TeamUsers",
    Base.metadata,
    Column("team_id", ForeignKey("Team.id")),
    Column("user_id", ForeignKey("User.id")),
)

AT_GamesTasks = Table(
    "GamesTasks",
    Base.metadata,
    Column("game_id", ForeignKey("Game.id")),
    Column("task_id", ForeignKey("Task.id")),
)

AT_GamesTeams = Table(
    "GamesTeams",
    Base.metadata,
    Column("game_id", ForeignKey("Game.id")),
    Column("team_id", ForeignKey("Team.id")),
)
