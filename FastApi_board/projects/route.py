from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import projects.functions
from projects.model import (Project,
                   ProjectList,
                   CreateProject,
                   EditProject,
                   ChangeArchiveStatus)


router = APIRouter(prefix='/to_do_list', tags=["Projects"])

@router.get('/project',
            status_code=200,
            response_model=Project)
async def get_project_details(project_id: int, session: AsyncSession = Depends(get_db)):
    return await projects.functions.get_project_details(project_id, session)


@router.post('/project',
             status_code=200,
             response_model=Project)
async def create_project(project: CreateProject, session: AsyncSession = Depends(get_db)):
    return await projects.functions.create_project(project, session)


@router.patch('/project',
              status_code=200,
              response_model_exclude_unset=True)
async def edit_project(project: EditProject, session: AsyncSession = Depends(get_db)):
    return await projects.functions.edit_project(project, session)


@router.put('/change_archive_status', status_code=200)
async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession = Depends(get_db)):
    return await projects.functions.change_archive_status(project, session)


@router.delete('/project', status_code=200)
async def delete_from_archive(project_id: int, session: AsyncSession = Depends(get_db)):
    return await projects.functions.delete_from_archive(project_id, session)


@router.get('/project_list', status_code=200,
            response_model=ProjectList)
async def get_projects(session: AsyncSession = Depends(get_db)):
    return await projects.functions.get_projects(session)