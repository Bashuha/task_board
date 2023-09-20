from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import sections.functions
from sections.model import (CreateSection,
                            EditSection,
                            SectionOrder,
                            NotFoundError,
                            BadRequestError)


router = APIRouter(tags=['Section'])


responses_dict = {404: {"model": NotFoundError,
                        "description": "Попытка создать раздел в несуществующем проекте"},
                  400: {"model": BadRequestError,
                        "description": "Ошибка при передаче неверного количества разделов"}}


@router.post('/section',
             status_code=status.HTTP_200_OK,
             responses={404: responses_dict[404]})
async def create_section(section: CreateSection, session: AsyncSession = Depends(get_db)):
    return await sections.functions.create_section(section, session)


@router.patch('/section', status_code=status.HTTP_200_OK)
async def edit_section(section: EditSection, session: AsyncSession = Depends(get_db)):
    return await sections.functions.edit_section(section, session)


@router.delete('/section', status_code=status.HTTP_200_OK)
async def delete_section(section_id: int, session: AsyncSession = Depends(get_db)):
    return await sections.functions.delete_section(section_id, session)


@router.put('/section_order',
            status_code=status.HTTP_200_OK,
            responses={400: responses_dict[400]})
async def change_section_order(section_order: SectionOrder, session: AsyncSession = Depends(get_db)):
    return await sections.functions.change_section_order(section_order, session)