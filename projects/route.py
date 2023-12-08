from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import projects.functions
from projects.model import (
    Project,
    IncomingTasks,
    ProjectList,
    CreateProject,
    EditProject,
    ChangeArchiveStatus,
    NotFoundError,
    BadRequestError
)


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
async def get_project_details(project_id: int = None, session: AsyncSession = Depends(get_db)):
    return await projects.functions.get_project_details(project_id, session)


@router.post('/project',
            status_code=status.HTTP_200_OK,
            responses={404: responses_dict[404]})
async def create_project(project: CreateProject, session: AsyncSession = Depends(get_db)):
    return await projects.functions.create_project(project, session)


@router.patch('/project', status_code=status.HTTP_200_OK)
async def edit_project(project: EditProject, session: AsyncSession = Depends(get_db)):
    return await projects.functions.edit_project(project, session)


@router.put('/change_archive_status',
            status_code=status.HTTP_200_OK,
            responses={404: responses_dict[404]})
async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession = Depends(get_db)):
    return await projects.functions.change_archive_status(project, session)


@router.delete('/project',
                status_code=status.HTTP_200_OK,
                responses={404: responses_dict[404],
                           400: responses_dict[400]})
async def delete_from_archive(project_id: int, session: AsyncSession = Depends(get_db)):
    return await projects.functions.delete_from_archive(project_id, session)


@router.get('/project_list',
            status_code=status.HTTP_200_OK,
            response_model=ProjectList)
async def get_projects(session: AsyncSession = Depends(get_db)):
    return await projects.functions.get_projects(session)