from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.teams.shemas import TeamCreate, TeamRead
from src.teams import crud as teams_crud
from src.auth.auth import current_user
router = APIRouter()


@router.get("/teams/{team_id}", summary="Get Team By Id", response_model=TeamRead,
            status_code=status.HTTP_200_OK, dependencies=[Depends(current_user)])
async def get_team(team_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)]):
    team = await teams_crud.get_team_data(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    return team


@router.post("/teams/create", summary="Create Team", response_model=TeamRead,
             status_code=status.HTTP_200_OK, dependencies=[Depends(current_user)])
async def create_team(team_data: Annotated[TeamCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    return await teams_crud.create_team(db, team_data)
