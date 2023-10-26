from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db_session
from src.teams.shemas import TeamCreate, TeamRead, TeamUpdate
from src.teams.models import Team as TeamModel
from src.teams.crud import TeamsCrud
from src.auth.auth import current_user
from src.auth.schemas import UserRead
from src.teams.utils import TeamsUserNotFound
from src.websockets.router import ws_events_manager

router = APIRouter()


@router.post("/teams",
             summary="Create Team",
             response_model=TeamRead,
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
                 status.HTTP_409_CONFLICT: {
                     "description": "A team with an already created name."}
             })
async def create_team(team_data: Annotated[TeamCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    check = await teams_crud.check_team_name_in_db(team_data.name)
    if check:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Team with name='{team_data.name}' already created.")
    db_team = await teams_crud.create_team(team_data, owner_id=user_request_data.id)
    await teams_crud.commit()
    await teams_crud.refresh(db_team)
    return db_team


@router.get("/teams/{team_id}",
            summary="Get Team By Id",
            response_model=TeamRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The team was not found."}
            })
async def get_team(team_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    return team


@router.get("/teams",
            summary="Get team by user",
            response_model=TeamRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The team or user was not found."}
            })
async def get_team(user_id: Annotated[int, Query()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    ans_user = await teams_crud.get_user_data(user_id)
    if user_request_data.is_superuser is False and user_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You have no rights to this information.")
    if ans_user is None or ans_user.team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user or the user's team were not found.")
    return ans_user.team


@router.delete("/teams/{team_id}",
               summary="Delete Team By Id",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The team was not found."}
               })
async def delete_team(team_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    await teams_crud.delete_team(team)
    await teams_crud.commit()
    return


@router.patch("/teams/{team_id}",
              summary="Update Team By Id",
              response_model=TeamRead,
              responses={
                  status.HTTP_200_OK: {
                      "description": "Successful Response"},
                  status.HTTP_403_FORBIDDEN: {
                      "description": "Access rights error."},
                  status.HTTP_404_NOT_FOUND: {
                      "description": "The team was not found."}
              })
async def update_team(team_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)],
                      new_team_data: Annotated[TeamUpdate, Body()]):
    teams_crud = TeamsCrud(db)
    team: TeamModel = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    update_data = new_team_data.dict(exclude_unset=True)
    team = await teams_crud.update_team(team, update_data)
    await teams_crud.commit()
    return team


@router.get("/teams/{team_id}/users",
            summary="Get Team's Users",
            response_model=list[UserRead],
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The team was not found."}
            })
async def get_team(team_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    return team.users


@router.post("/teams/{team_id}/users/sendjoinrequest",
             summary="Send a request to the user to join the team",
             response_model=None,
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Access rights error."},
                 status.HTTP_404_NOT_FOUND: {
                     "description": "The team or user were not found."},
                 status.HTTP_409_CONFLICT: {
                     "description": "The user is already in the team."}
             })
async def add_user_to_team_request(team_id: Annotated[int, Path()],
                                   user_email: Annotated[str, Query()],
                                   db: Annotated[AsyncSession, Depends(get_db_session)],
                                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    user = await teams_crud.get_user_data_by_email(user_email=user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email={user_email} not found.")
    if user.team is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The user with email={user_email} has already been "
                                   f"added to the team with ID={user.team.id}")
    team_request_event = {
        "type": "JoinTeamRequestEvent",
        "team_id": team_id,
        "request_from_user_id": user_request_data.id
    }
    await ws_events_manager.send_message(user.id, message=team_request_event)


@router.post("/teams/{team_id}/users",
             summary="Join the team",
             response_model=list[UserRead],
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
                 status.HTTP_403_FORBIDDEN: {
                     "description": "Access rights error."},
                 status.HTTP_404_NOT_FOUND: {
                     "description": "The team or user were not found."},
                 # status.HTTP_409_CONFLICT: {
                 #     "description": "The user is already in the team."}
             })
async def add_user_to_team(team_id: Annotated[int, Path()],
                           db: Annotated[AsyncSession, Depends(get_db_session)],
                           user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team: TeamModel = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    # if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f"You do not have access rights to the team with id={team_id}")
    await teams_crud.add_user_to_team(team, user_request_data.id)
    await teams_crud.commit()
    await teams_crud.refresh(team)
    return team.users


@router.delete("/teams/{team_id}/users/{user_id}",
               summary="Remove a user from a team",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The team or user was not found."}
               })
async def remove_user_from_team(team_id: Annotated[int, Path()],
                                user_id: Annotated[int, Path()],
                                db: Annotated[AsyncSession, Depends(get_db_session)],
                                user_request_data: Annotated[UserRead, Depends(current_user)]):
    teams_crud = TeamsCrud(db)
    team: TeamModel = await teams_crud.get_team_data(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Team with id={team_id} not found.")
    if user_request_data.is_superuser is False and team.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the team with id={team_id}")
    try:
        await teams_crud.remove_user_from_team(team, user_id)
    except TeamsUserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user with ID={user_id} was not found in the team with ID={team_id}")
    else:
        await teams_crud.commit()
    return
