from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db_session
from src.tasks.shemas import TaskCreate, TaskRead, TaskUpdate
from src.tasks.models import Task as TaskModel
from src.tasks.crud import TasksCrud
from src.auth.auth import current_user
from src.auth.schemas import UserRead

router = APIRouter()


@router.post("/tasks",
             summary="Create task",
             response_model=TaskRead,
             responses={
                 status.HTTP_201_CREATED: {
                     "description": "Successful Response"},
             })
async def create_task(task_data: Annotated[TaskCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    task_crud = TasksCrud(db)
    db_task = await task_crud.create_task(task_data, owner_id=user_request_data.id)
    await task_crud.commit()
    await task_crud.refresh(db_task)
    return db_task


@router.get("/tasks/{task_id}",
            summary="Get Task By Id",
            response_model=TaskRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The task was not found."}
            })
async def get_task(task_id: Annotated[int, Path()],
                   db: Annotated[AsyncSession, Depends(get_db_session)],
                   user_request_data: Annotated[UserRead, Depends(current_user)]):
    task_crud = TasksCrud(db)
    task = await task_crud.get_task_data(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    if user_request_data.is_superuser is False and task.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the task with id={task_id}")
    return task


@router.get("/tasks",
            summary="Get user's tasks",
            response_model=list[TaskRead],
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The task or user was not found."}
            })
async def get_tasks(user_id: Annotated[int, Query()],
                    db: Annotated[AsyncSession, Depends(get_db_session)],
                    user_request_data: Annotated[UserRead, Depends(current_user)]):
    task_crud = TasksCrud(db)
    ans_user = await task_crud.get_user_data(user_id)
    if user_request_data.is_superuser is False and user_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You have no rights to this information.")
    if ans_user is None or len(ans_user.tasks) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user or the user's tasks were not found.")
    return ans_user.tasks


@router.delete("/tasks/{task_id}",
               summary="Delete Task By Id",
               response_model=None,
               responses={
                   status.HTTP_204_NO_CONTENT: {
                       "description": "Successful Response"},
                   status.HTTP_403_FORBIDDEN: {
                       "description": "Access rights error."},
                   status.HTTP_404_NOT_FOUND: {
                       "description": "The task was not found."}
               })
async def delete_task(task_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)]):
    task_crud = TasksCrud(db)
    task = await task_crud.get_task_data(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    if user_request_data.is_superuser is False and task.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the task with id={task_id}")
    await task_crud.delete_task(task)
    await task_crud.commit()
    return


@router.patch("/tasks/{task_id}",
              summary="Update Task By Id",
              response_model=TaskRead,
              responses={
                  status.HTTP_200_OK: {
                      "description": "Successful Response"},
                  status.HTTP_403_FORBIDDEN: {
                      "description": "Access rights error."},
                  status.HTTP_404_NOT_FOUND: {
                      "description": "The task was not found."}
              })
async def update_task(task_id: Annotated[int, Path()],
                      db: Annotated[AsyncSession, Depends(get_db_session)],
                      user_request_data: Annotated[UserRead, Depends(current_user)],
                      new_task_data: Annotated[TaskUpdate, Body()]):
    task_crud = TasksCrud(db)
    task: TaskModel = await task_crud.get_task_data(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    if user_request_data.is_superuser is False and task.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the task with id={task_id}")
    update_data = new_task_data.dict(exclude_unset=True)
    task = await task_crud.update_task(task, update_data)
    await task_crud.commit()
    return task


@router.get("/tasks/{task_id}/user",
            summary="Get Task's Owner",
            response_model=UserRead,
            responses={
                status.HTTP_200_OK: {
                    "description": "Successful Response"},
                status.HTTP_403_FORBIDDEN: {
                    "description": "Access rights error."},
                status.HTTP_404_NOT_FOUND: {
                    "description": "The task was not found."}
            })
async def get_tasks_user(task_id: Annotated[int, Path()],
                         db: Annotated[AsyncSession, Depends(get_db_session)],
                         user_request_data: Annotated[UserRead, Depends(current_user)]):
    task_crud = TasksCrud(db)
    task: TaskModel = await task_crud.get_task_data(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    if user_request_data.is_superuser is False and task.owner_id != user_request_data.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have access rights to the task with id={task_id}")
    return task.user
