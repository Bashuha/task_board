from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import tasks.functions as task_func
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


@router.get(
    '/task',
    status_code=status.HTTP_200_OK,
    response_model=Task,
    responses={404: responses_dict[404]},
    summary='Получение детализации задачи, в которой ты владелец'    
)
async def get_task_details(
    task_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.get_task_details(task_id, session, user)


@router.post(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Создание задачи'
)
async def create_task(
    task: CreateTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.create_task(task, session, user)


@router.patch(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: {
        "model": ErrorNotFound,
        "description": error_description
    }},
    summary='Редактирование своей задачи'
)
async def edit_task(
    task: EditTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.edit_task(task, session, user)


@router.delete(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Удаление своей задачи'    
)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.delete_task(task_id, session, user)


@router.put(
    '/task_order',
    status_code=status.HTTP_200_OK,
    summary='Изменение порядка своих задач'    
)
async def change_task_order(
    task_order: TaskOrder,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.change_task_order(task_order, session, user)