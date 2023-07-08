from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.games.models import Game
from src.games.utils import GamesTaskNotFound, GamesTeamNotFound, TeamNotFound, TaskNotFound
from src.auth.models import User
from src.tasks.models import Task
from src.teams.models import Team


class GamesCrud:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_game_data(self, game_id: int) -> Game:
        """ Возвращает данные игры.  """
        query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_game_data_with_tasks(self, game_id: int) -> Game:
        """ Возвращает данные игры.  """
        query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user), selectinload(Game.tasks))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_task_to_game(self, game: Game, task_id: int):
        """ Добавляет загадку в игру. """
        query = select(Task).filter(Task.id == task_id)
        result = await self.db.execute(query)
        task = result.scalars().first()
        if task is not None:
            game.tasks.append(task)
        else:
            raise TaskNotFound
        return

    async def remove_task_from_game(self, game: Game, task_id: int):
        """ Удаляет загадку из игры. """
        flag = False
        for games_task in game.tasks:
            if games_task.id == task_id:
                game.tasks.remove(games_task)
                flag = True
        if not flag:
            raise GamesTaskNotFound
        return

    async def get_game_data_with_teams(self, game_id: int) -> Game:
        """ Возвращает данные игры.  """
        query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user), selectinload(Game.teams))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_team_to_game(self, game: Game, team_id: int):
        """ Добавляет команду в игру. """
        query = select(Team).filter(Team.id == team_id)
        result = await self.db.execute(query)
        team = result.scalars().first()
        if team is not None:
            game.teams.append(team)
        else:
            raise TeamNotFound
        return

    async def remove_team_from_game(self, game: Game, team_id: int):
        """ Удаляет команду из игры. """
        flag = False
        for games_team in game.teams:
            if games_team.id == team_id:
                game.teams.remove(games_team)
                flag = True
        if not flag:
            raise GamesTeamNotFound
        return

    async def create_game(self, game_data, owner_id):
        """ Создаёт запись игры в БД.  """
        db_game = Game(**game_data.dict(), owner_id=owner_id)
        self.db.add(db_game)
        return db_game

    async def delete_game(self, game: Game):
        """ Удаляет запись игры из БД.  """
        await self.db.delete(game)
        await self.db.commit()
        return game

    async def update_game(self, game: Game, update_data: dict):
        """ Обновляет информация об игре. """
        for key, value in update_data.items():
            setattr(game, key, value)
        await self.db.commit()
        return game

    async def get_user_data(self, user_id: int) -> User:
        """ Возвращает данные пользователя вместе с созданными им играми.  """
        query = select(User).filter(User.id == user_id).options(selectinload(User.games))  # TODO: .limit(10)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance: object):
        await self.db.refresh(instance)
