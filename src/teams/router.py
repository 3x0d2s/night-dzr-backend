from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.teams.shemas import TeamCreate, TeamRead
from src.teams import crud as teams_crud
from src.auth.auth import current_user
from src.auth.schemas import UserRead
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
