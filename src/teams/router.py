from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db_session
from src.teams.shemas import TeamCreate, TeamRead, TeamUpdate
from src.teams.models import Team as TeamModel
from src.teams import crud as teams_crud
from src.auth.auth import current_user
from src.auth.schemas import UserRead
from src.teams.utils import TeamsUserNotFound

router = APIRouter()


@router.get("/teams/{team_id}", summary="Get Team By Id",
            response_model=TeamRead, status_code=status.HTTP_200_OK)
async def get_team(team_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user: Annotated[UserRead, Depends(current_user)]):
    team = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    return team


@router.post("/teams/create", summary="Create Team",
             response_model=TeamRead, status_code=status.HTTP_200_OK)
async def create_team(team_data: Annotated[TeamCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user: Annotated[UserRead, Depends(current_user)]):
    check = await teams_crud.check_team_name_in_db(db, team_data.name)
    if check:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Team with name='{team_data.name}' already created.")
    return await teams_crud.create_team(db, team_data, owner_id=user.id)


@router.delete("/teams/{team_id}", summary="Delete Team By Id",
               response_model=TeamRead, status_code=status.HTTP_200_OK)
async def delete_team(team_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user: Annotated[UserRead, Depends(current_user)]):
    team = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    return await teams_crud.delete_team(db, team)


@router.patch("/teams/{team_id}", summary="Update Team By Id",
              response_model=TeamRead, status_code=status.HTTP_200_OK)
async def update_team(team_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user: Annotated[UserRead, Depends(current_user)],
                      new_team_data: Annotated[TeamUpdate, Body()]):
    team: TeamModel = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    update_data = new_team_data.dict(exclude_unset=True)
    return await teams_crud.update_team(db, team, update_data)


@router.get("/teams/users/{team_id}", summary="Get Team's Users",
            response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_team(team_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user: Annotated[UserRead, Depends(current_user)]):
    team = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    return team.users


@router.post("/teams/users/{team_id}", summary="Add a user to a team",
             response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def add_user_to_team(team_id: Annotated[int, Path()],
                           db: Annotated[AsyncSession, Depends(get_db_session)],
                           user: Annotated[UserRead, Depends(current_user)],
                           new_user_id: Annotated[int, Query()]):
    team: TeamModel = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    for team_user in team.users:
        if team_user.id == new_user_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"The user with ID={new_user_id} has already been "
                                       f"added to the team with ID={team_id}")
    await teams_crud.add_user_to_team(db, team, new_user_id)
    return team.users


@router.delete("/teams/users/{team_id}", summary="Remove a user from a team",
               response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def add_user_to_team(team_id: Annotated[int, Path()],
                           db: Annotated[AsyncSession, Depends(get_db_session)],
                           user: Annotated[UserRead, Depends(current_user)],
                           user_id: Annotated[int, Query()]):
    team: TeamModel = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user.is_superuser is False and team.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    try:
        await teams_crud.remove_user_from_team(db, team, user_id)
    except TeamsUserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user with ID={user_id} was not found in the team with ID={team_id}")
    return team.users


@router.get("/teams/byuser/{user_id}", summary="Get team by user",
            response_model=TeamRead, status_code=status.HTTP_200_OK)
async def get_team(user_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user: Annotated[UserRead, Depends(current_user)]):
    ans_user = await teams_crud.get_user_data(db, user_id)
    if user.is_superuser is False and user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You have no rights to this information.")
    if ans_user is None or ans_user.team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user or the user's team were not found.")
    return ans_user.team
