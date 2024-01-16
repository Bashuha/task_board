from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import comments.functions as comment_func
from users.functions import get_current_user
from database.schemas import UserInfo
from comments.model import CreateComment, EditComment, NotFoundError


router = APIRouter(tags=['Comment'])


@router.post(
    '/comment',
    status_code=status.HTTP_200_OK,
    responses={404: {
        "model": NotFoundError,
        "description": "Попытка добавить комент к несуществующей задаче"
    }},
    summary='Создание комментария'
)
async def create_comment(
    comment: CreateComment,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await comment_func.create_comment(comment, session, user)


@router.put(
    '/comment',
    status_code=status.HTTP_200_OK,
    summary='Редактирование комментария'
)
async def edit_comment(
    comment: EditComment,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await comment_func.edit_comment(comment, session, user)


@router.delete(
    '/comment',
    status_code=status.HTTP_200_OK,
    summary='Удаление комментария'
)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await comment_func.delete_comment(comment_id, session, user)