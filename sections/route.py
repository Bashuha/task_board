from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import sections.functions as section_func
from sections.model import (
    CreateSection,
    EditSection,
    SectionOrder,
    NotFoundError,
    BadRequestError,
    DeleteSection
)
from users.functions import get_current_user
from database.schemas import UserInfo


router = APIRouter(tags=['Section'])


responses_dict = {404: {"model": NotFoundError,
                        "description": "Попытка создать раздел в несуществующем проекте"},
                  400: {"model": BadRequestError,
                        "description": "Ошибка при передаче неверного количества разделов"}}


@router.post(
    '/section',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Создание раздела'    
)
async def create_section(
    section: CreateSection,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await section_func.create_section(section, session, user)


@router.patch(
    '/section',
    status_code=status.HTTP_200_OK,
    summary='Редактирование раздела'
)
async def edit_section(
    section: EditSection,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await section_func.edit_section(section, session, user)


@router.delete(
    '/section',
    status_code=status.HTTP_200_OK,
    summary='Удаление раздела'    
)
async def delete_section(
    section: DeleteSection,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await section_func.delete_section(section, session, user)


@router.put(
    '/section_order',
    status_code=status.HTTP_200_OK,
    responses={400: responses_dict[400]},
    summary='Изменение порядка разделов в конкретном проекте'
)
async def change_section_order(
    section_order: SectionOrder,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await section_func.change_section_order(section_order, session, user)