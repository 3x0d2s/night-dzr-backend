from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db_session
from src.games.shemas import GameCreate, GameRead, GameUpdate
from src.games.models import Game as GameModel
from src.games.utils import GamesTaskNotFound, GamesTeamNotFound, TeamNotFound, TaskNotFound
from src.games.crud import GamesCrud
from src.auth.auth import current_user
from src.auth.schemas import UserRead
from src.tasks.shemas import TaskRead
from src.teams.shemas import TeamRead

router = APIRouter()


@router.post("/games",
             summary="Create game",
             response_model=GameRead,
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
             })
async def create_game(game_data: Annotated[GameCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    db_game = await game_crud.create_game(game_data, owner_id=user_request_data.id)
    await game_crud.commit()
    await game_crud.refresh(db_game)
    return db_game


@router.get("/games/{game_id}",
            summary="Get Game By Id",
            response_model=GameRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The game was not found."}
            })
async def get_game(game_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game = await game_crud.get_game_data(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    return game


@router.get("/games",
            summary="Get user's games",
            response_model=list[GameRead],
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The game or user was not found."}
            })
async def get_games(user_id: Annotated[int, Query()],
                    db: Annotated[AsyncSession, Depends(get_db_session)],
                    user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    ans_user = await game_crud.get_user_data(user_id)
    if user_request_data.is_superuser is False and user_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You have no rights to this information.")
    if ans_user is None or len(ans_user.games) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user or the user's games were not found.")
    return ans_user.games


@router.delete("/games/{game_id}",
               summary="Delete Game By Id",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The game was not found."}
               })
async def delete_game(game_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game = await game_crud.get_game_data(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    await game_crud.delete_game(game)
    await game_crud.commit()
    return


@router.patch("/games/{game_id}",
              summary="Update Game By Id",
              response_model=GameRead,
              responses={
                  status.HTTP_200_OK: {
                      "description": "Successful Response"},
                  status.HTTP_403_FORBIDDEN: {
                      "description": "Access rights error."},
                  status.HTTP_404_NOT_FOUND: {
                      "description": "The game was not found."}
              })
async def update_game(game_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)],
                      new_game_data: Annotated[GameUpdate, Body()]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    update_data = new_game_data.dict(exclude_unset=True)
    game = await game_crud.update_game(game, update_data)
    await game_crud.commit()
    return game


@router.get("/games/{game_id}/user",
            summary="Get Game's Owner",
            response_model=UserRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The game was not found."}
            })
async def get_games_user(game_id: Annotated[int, Path()],
                         db: Annotated[AsyncSession, Depends(get_db_session)],
                         user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    return game.user


@router.get("/games/{game_id}/tasks",
            summary="Get Game's Tasks",
            response_model=list[TaskRead],
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The game was not found."}
            })
async def get_games_tasks(game_id: Annotated[int, Path()],
                          db: Annotated[AsyncSession, Depends(get_db_session)],
                          user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data_with_tasks(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    return game.tasks


@router.post("/games/{game_id}/tasks",
             summary="Add a task to a game",
             response_model=list[TaskRead],
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Access rights error."},
                 status.HTTP_404_NOT_FOUND: {
                     "description": "The game or task was not found."},
                 status.HTTP_409_CONFLICT: {
                     "description": "The riddle has already been added to the game."}
             })
async def add_task_to_game(game_id: Annotated[int, Path()],
                           task_id: Annotated[int, Query()],
                           db: Annotated[AsyncSession, Depends(get_db_session)],
                           user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data_with_tasks(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}.")
    for games_task in game.tasks:
        if games_task.id == task_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"The task with ID={task_id} has already been "
                                       f"added to the game with ID={game_id}.")
    try:
        await game_crud.add_task_to_game(game, task_id)
    except TaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    else:
        await game_crud.commit()
    return game.tasks


@router.delete("/games/{game_id}/tasks/{task_id}",
               summary="Remove a task from a game",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The game or task was not found."}
               })
async def remove_task_from_game(game_id: Annotated[int, Path()],
                                task_id: Annotated[int, Path()],
                                db: Annotated[AsyncSession, Depends(get_db_session)],
                                user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data_with_tasks(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    try:
        await game_crud.remove_task_from_game(game, task_id)
    except GamesTaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The task with ID={task_id} was not found in the game with ID={game_id}")
    else:
        await game_crud.commit()
    return


@router.get("/games/{game_id}/teams",
            summary="Get Game's Teams",
            response_model=list[TeamRead],
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The game was not found."}
            })
async def get_games_teams(game_id: Annotated[int, Path()],
                          db: Annotated[AsyncSession, Depends(get_db_session)],
                          user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game: GameModel = await game_crud.get_game_data_with_teams(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    return game.teams


@router.post("/games/{game_id}/teams",
             summary="Add a team to a game",
             response_model=list[TeamRead],
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Access rights error."},
                 status.HTTP_404_NOT_FOUND: {
                     "description": "The game or team was not found."},
                 status.HTTP_409_CONFLICT: {
                     "description": "The teams has already been added to the game."}
             })
async def add_team_to_game(game_id: Annotated[int, Path()],
                           team_id: Annotated[int, Query()],
                           db: Annotated[AsyncSession, Depends(get_db_session)],
                           user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game = await game_crud.get_game_data_with_teams(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}.")
    for games_team in game.teams:
        if games_team.id == team_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"The task with ID={team_id} has already been "
                                       f"added to the game with ID={game_id}.")
    try:
        await game_crud.add_team_to_game(game, team_id)
    except TeamNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    else:
        await game_crud.commit()
    return game.teams


@router.delete("/games/{game_id}/teams/{team_id}",
               summary="Remove a team from a game",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The game or team was not found."}
               })
async def remove_team_from_game(game_id: Annotated[int, Path()],
                                team_id: Annotated[int, Path()],
                                db: Annotated[AsyncSession, Depends(get_db_session)],
                                user_request_data: Annotated[UserRead, Depends(current_user)]):
    game_crud = GamesCrud(db)
    game = await game_crud.get_game_data_with_teams(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id={game_id} not found.")
    if user_request_data.is_superuser is False and game.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the game with id={game_id}")
    try:
        await game_crud.remove_team_from_game(game, team_id)
    except GamesTeamNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The team with ID={team_id} was not found in the game with ID={game_id}")
    else:
        await game_crud.commit()
    return
