from database.my_engine import get_db
from database.schemas import UserInfo
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import projects.functions as project_func
from projects.model import (
    Project,
    IncomingTasks,
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


@router.get('/project',
            status_code=status.HTTP_200_OK,
            response_model=Project | IncomingTasks,
            responses={404: responses_dict[404]})
async def get_project_details(
    project_id: int = None,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.get_project_details(project_id, session)


@router.get('/project_details',
            status_code=status.HTTP_200_OK,
            response_model=ProjectDetails | IncomingTasks,
            responses={404: responses_dict[404]})
async def new_project_details(
    project_id: int = None,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.project_details(project_id, session, user)


@router.post('/project',
            status_code=status.HTTP_200_OK,
            responses={404: responses_dict[404]})
async def create_project(
    project: CreateProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.create_project(project, user, session)


@router.patch('/project', status_code=status.HTTP_200_OK)
async def edit_project(
    project: EditProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.edit_project(project, session, user)


@router.put('/change_archive_status',
            status_code=status.HTTP_200_OK,
            responses={404: responses_dict[404]})
async def change_archive_status(
    project: ChangeArchiveStatus,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.change_archive_status(project, session, user)


@router.delete('/project',
                status_code=status.HTTP_200_OK,
                responses={404: responses_dict[404],
                           400: responses_dict[400]})
async def delete_from_archive(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.delete_from_archive(project_id, session, user)


@router.get('/project_list',
            status_code=status.HTTP_200_OK,
            response_model=ProjectList)
async def get_projects(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.get_projects(user, session)


@router.get('/today_tasks',
            status_code=status.HTTP_200_OK,
            response_model=TodayTaskList)
async def get_today_tasks(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await project_func.get_today_tasks(session, user)