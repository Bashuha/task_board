from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import functions.task_func
from type_model import Task

router = APIRouter(prefix='/to_do_list', tags=['Task'])


@router.get('/task', status_code=200)
async def get_task_details(task_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.task_func.get_task_details(task_id, session)

@router.post('/task', status_code=200)
async def create_task(task: Task, session: AsyncSession = Depends(get_db)):
    return await functions.task_func.create_task(task, session)

@router.patch('/task', status_code=200)
async def edit_task(task: Task, session: AsyncSession = Depends(get_db)):
    return await functions.task_func.edit_task(task, session)

@router.delete('/task', status_code=200)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_db)):
    return await functions.task_func.delete_task(task_id, session)
