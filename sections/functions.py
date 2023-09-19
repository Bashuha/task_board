from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sections.model import CreateSection, EditSection, SectionOrder
from fastapi import HTTPException
from database.schemas import Project, Sections


async def create_section(section: CreateSection, session: AsyncSession):
    project_qr = session.get(Project, section.project_id)
    project: Project = await project_qr
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден')
    
    section_data = section.model_dump()
    section_data['order_number'] = len(project.Sections) + 1
    stmt = insert(Sections).values(section_data)
    await session.execute(stmt)
    await session.commit()


async def edit_section(section: EditSection, session: AsyncSession):
    section_data = section.model_dump(exclude={'id'})
    update_query = update(Sections).where(Sections.id == section.id).values(section_data)
    await session.execute(update_query)
    await session.commit()


async def delete_section(section_id: int, session: AsyncSession):
    section_qr = session.get(Sections, section_id)
    section: Sections = await section_qr
    if not section:
        raise HTTPException(detail='Раздел не найдена', status_code=404)
    
    delete_query = delete(Sections).where(Sections.id == section_id)
    await session.execute(delete_query)
    await session.commit()


async def change_section_order(section_order: SectionOrder, session: AsyncSession):
    new_order_list = list()
    sections_qr = select(Sections).where(Sections.project_id == section_order.project_id)
    section_list_model = await session.execute(sections_qr)
    section_order_list = section_list_model.scalars().all()
    if len(section_order.sections) != len(section_order_list):
        raise HTTPException(status_code=400, detail="Неверный формат данных")
    # создаем словарь из нового списка id и генерируем новый порядковый номер
    for number, sec_id in enumerate(section_order.sections, start=1):
        order_dict = {"id": sec_id.id, "order_number": number}
        # добавляем полученный словарь в список для UPDATE
        new_order_list.append(order_dict)
    # одним запросом обновляем порядок, используя наш список словарей
    await session.execute(update(Sections).where(Sections.project_id==section_order.project_id), new_order_list, execution_options={"synchronize_session": False})
    await session.commit()
    # мы исользовали "массовое обновление по первичному ключу" и из-за того, что мы 
    # добавили дополнительный "where" критерий в виде project_id, нам необходимо
    # прописать execution_options