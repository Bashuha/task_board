from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import functions.project_func
from type_model import Project, ProjectList


router = APIRouter(prefix='/to_do_list', tags=["Projects"])

@router.get('/project', status_code=200,
            response_model=Project,
            response_model_exclude_unset=True)
async def get_project_details(project_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.project_func.get_project_details(project_id, session)

@router.post('/project', status_code=200)
async def create_project(project: Project, session: AsyncSession = Depends(get_db)):
    return await functions.project_func.create_project(project, session)

@router.patch('/project', status_code=200)
async def edit_project(project: Project, session: AsyncSession = Depends(get_db)):
    return await functions.project_func.edit_project(project, session)

@router.put('/change_archive_status', status_code=200)
async def change_archive_status(project: Project, session: AsyncSession = Depends(get_db)):
    return await functions.project_func.change_archive_status(project, session)

@router.delete('/project', status_code=200)
async def delete_from_archive(project_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.project_func.delete_from_archive(project_id, session)

@router.get('/project_list', status_code=200,
            response_model=ProjectList,
            response_model_exclude_unset=True)
async def get_projects(session: AsyncSession = Depends(get_db)):
    return await functions.project_func.get_projects(session)