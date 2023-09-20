from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import tasks.functions
from tasks.model import Task, CreateTask, EditTask, ErrorNotFound


router = APIRouter(tags=['Task'])


error_description = """
Причины возникновения

1. Введен неверный **id** задачи
2. Введен неверный **id** проекта
3. Введен неверный **id** раздела
"""


responses_dict = {404: {"model": ErrorNotFound,
                        "description": "The task not found"}}


@router.get('/task',
            status_code=status.HTTP_200_OK,
            response_model=Task,
            responses={404: responses_dict[404]})
async def get_task_details(task_id: int, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.get_task_details(task_id, session)


@router.post('/task',
             status_code=status.HTTP_200_OK,
             responses={404: responses_dict[404]})
async def create_task(task: CreateTask, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.create_task(task, session)


@router.patch('/task',
              status_code=status.HTTP_200_OK,
              responses={
                    404: {"model": ErrorNotFound,
                          "description": error_description}})
async def edit_task(task: EditTask, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.edit_task(task, session)


@router.delete('/task',
               status_code=status.HTTP_200_OK,
               responses={404: responses_dict[404]})
async def delete_task(task_id: int, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.delete_task(task_id, session)
