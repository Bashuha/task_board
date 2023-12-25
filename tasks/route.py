from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import tasks.functions
from tasks.model import Task, CreateTask, EditTask, ErrorNotFound, TaskOrder
from users.functions import get_current_user
from database.schemas import UserInfo


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
async def create_task(
    task: CreateTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await tasks.functions.create_task(task, session, user)


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


@router.put('/task_order',
            status_code=status.HTTP_200_OK)
async def change_task_order(task_order: TaskOrder, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.change_task_order(task_order, session)