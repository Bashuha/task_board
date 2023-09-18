from database.my_engine import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import sections.functions
from sections.model import CreateSection, EditSection, SectionOrder


router = APIRouter(prefix='/to_do_list', tags=['Section'])

@router.post('/section', status_code=200)
async def create_section(section: CreateSection, session: AsyncSession = Depends(get_db)):
    return await sections.functions.create_section(section, session)


@router.patch('/section', status_code=200)
async def edit_section(section: EditSection, session: AsyncSession = Depends(get_db)):
    return await sections.functions.edit_section(section, session)


@router.delete('/section', status_code=200)
async def delete_section(section_id: int, session: AsyncSession = Depends(get_db)):
    return await sections.functions.delete_section(section_id, session)


@router.put('/section_order', status_code=200)
async def change_section_order(section_order: SectionOrder, session: AsyncSession = Depends(get_db)):
    return await sections.functions.change_section_order(section_order, session)