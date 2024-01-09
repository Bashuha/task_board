from database.my_engine import get_db
from database.schemas import UserInfo
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import projects.functions as project_func
from projects.model import (
    ProjectList,
    CreateProject,
    EditProject,
    ChangeArchiveStatus,
    NotFoundError,
    BadRequestError,
    TodayTaskList,
    ProjectDetails
)
from users.functions import get_current_user


router = APIRouter(tags=["Projects"])


responses_dict = {
    404: {
        "model": NotFoundError,
        "description": "Введен не верный id проекта"
    },
    400: {
        "model": BadRequestError,
        "description": "Попытка удалить не архивированный проект"
    }
}


@router.get(
    '/project_details',
    status_code=status.HTTP_200_OK,
    response_model=ProjectDetails,
    responses={404: responses_dict[404]},
    summary='Получение детализации проекта'
)
async def project_details(
    project_id: int = None,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.project_details(project_id, session, user)


@router.post(
    '/project',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Создание нового проекта'
)
async def create_project(
    project: CreateProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.create_project(project, user, session)


@router.patch(
    '/project',
    status_code=status.HTTP_200_OK,
    summary='Редактирование проекта'
)
async def edit_project(
    project: EditProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.edit_project(project, session, user)


@router.put(
    '/change_archive_status',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Перемещение проекта в архив/из архива'
)
async def change_archive_status(
    project: ChangeArchiveStatus,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.change_archive_status(project, session, user)


@router.delete(
    '/project',
    status_code=status.HTTP_200_OK,
    responses={
        404: responses_dict[404],
        400: responses_dict[400]
    },
    summary='Удаление своего проекта'
)
async def delete_from_archive(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.delete_from_archive(project_id, session, user)


@router.get(
    '/project_list',
    status_code=status.HTTP_200_OK,
    response_model=ProjectList,
    summary='Получение своих проектов'
)
async def get_projects(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.get_projects(user, session)


@router.get(
    '/today_tasks',
    status_code=status.HTTP_200_OK,
    response_model=TodayTaskList,
    summary='Получение своих задач на сегодня'
)
async def get_today_tasks(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await project_func.get_today_tasks(session, user)