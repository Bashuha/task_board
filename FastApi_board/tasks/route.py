from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import tasks.functions
from tasks.model import Task, CreateTask, EditTask

router = APIRouter(prefix='/to_do_list', tags=['Task'])


@router.get('/task', status_code=200, response_model=Task)
async def get_task_details(task_id: int, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.get_task_details(task_id, session)


@router.post('/task', status_code=200)
async def create_task(task: CreateTask, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.create_task(task, session)


@router.patch('/task', status_code=200)
async def edit_task(task: EditTask, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.edit_task(task, session)


@router.delete('/task', status_code=200)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_db)):
    return await tasks.functions.delete_task(task_id, session)
