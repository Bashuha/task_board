from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import functions
from type_model import Project

router = APIRouter(prefix='/to_do_list')

@router.get('/project', status_code=200)
async def get_project_details(project_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.get_project_details(project_id, session)

@router.post('/project', status_code=200)
async def create_project(project: Project, session: AsyncSession = Depends(get_db)):
    return await functions.create_project(project, session)

@router.patch('/project', status_code=200)
async def edit_project(project: Project, session: AsyncSession = Depends(get_db)):
    return await functions.edit_project(project, session)

@router.put('/change_archive_status', status_code=200)
async def change_archive_status(project: Project, session: AsyncSession = Depends(get_db)):
    pass

@router.delete('/project', status_code=200)
async def delete_from_archive(project_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.delete_from_archive(project_id, session)