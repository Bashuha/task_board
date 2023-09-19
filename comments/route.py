from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import comments.functions
from comments.model import CreateComment, EditComment


router = APIRouter(tags=['Comment'])


@router.post('/comment', status_code=200)
async def create_comment(comment: CreateComment, session: AsyncSession = Depends(get_db)):
    return await comments.functions.create_comment(comment, session)


@router.put('/comment', status_code=200)
async def edit_comment(comment: EditComment, session: AsyncSession = Depends(get_db)):
    return await comments.functions.edit_comment(comment, session)


@router.delete('/comment', status_code=200)
async def delete_comment(comment_id: int, session: AsyncSession = Depends(get_db)):
    return await comments.functions.delete_comment(comment_id, session)