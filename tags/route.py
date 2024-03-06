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


@router.patch(
    '/edit_tag',
    status_code=status.HTTP_200_OK,
    summary='Редактирование тега'
)
async def edit_tag(
    tag_model: tag_model.EditTag,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await tag_func.edit_tag(session, tag_model, user)


@router.delete(
    "/delete_tag",
    status_code=status.HTTP_200_OK,
    summary="Удаление тега"
)
async def delete_tag(
    tag_model: tag_model.DeleteTag,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await tag_func.delete_tag(session, tag_model, user)


@router.post(
    '/add_tag',
    status_code=status.HTTP_200_OK,
    summary="Добавление тега к задаче"
)
async def add_tag_to_task(
    tag_model: tag_model.ManageTag,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await tag_func.add_tag_to_task(session, tag_model, user)


@router.delete(
    '/remove_tag_task',
    status_code=status.HTTP_200_OK,
    summary="Удаление тега из задачи"
)
async def remove_tag_from_task(
    tag_model: tag_model.ManageTag,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await tag_func.remove_tag_from_task(session, tag_model, user)