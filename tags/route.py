from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import tags.functions as tag_func
import tags.model as tag_model
from users.functions import get_current_user
from database.schemas import UserInfo


router = APIRouter(tags=['Tag'])


@router.get(
    '/tag_list',
    status_code=status.HTTP_200_OK,
    response_model=tag_model.TagList,
    summary='Получение всех тегов проекта'
)
async def get_tag_list(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user),
):
    return await tag_func.get_tag_list(session, user, project_id)


@router.post(
    '/create_tag',
    status_code=status.HTTP_201_CREATED,
    summary='Создание тега'
)
async def get_tag_list(
    tag_model: tag_model.CreateTag,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user),
):
    return await tag_func.create_tag(session, tag_model, user)