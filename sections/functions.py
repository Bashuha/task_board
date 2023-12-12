from sqlalchemy.orm import load_only, joinedload
from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sections.model import CreateSection, EditSection, SectionOrder
from fastapi import HTTPException, status
from database.schemas import Project, Sections


async def create_section(section: CreateSection, session: AsyncSession):
    project_query = await session.execute(
        select(Project).
            options(
                load_only(Project.id),
                joinedload(Project.sections).load_only(Sections.id)
            ).
        where(Project.id == section.project_id)
    )
    project = project_query.unique().scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден')
    
    section_data = section.model_dump()
    section_data['order_number'] = len(project.sections) + 1
    stmt = insert(Sections).values(section_data)
    await session.execute(stmt)
    await session.commit()


async def edit_section(section: EditSection, session: AsyncSession):
    section_data = section.model_dump(exclude={'id'})
    update_query = update(Sections).where(Sections.id == section.id).values(section_data)
    await session.execute(update_query)
    await session.commit()


async def delete_section(section_id: int, session: AsyncSession):
    delete_query = delete(Sections).where(Sections.id == section_id)
    await session.execute(delete_query)
    await session.commit()


async def change_section_order(section_order: SectionOrder, session: AsyncSession):
    new_order_list = list()
    sections_qr = select(Sections).where(Sections.project_id == section_order.project_id)
    section_list_model = await session.execute(sections_qr)
    section_order_list = section_list_model.unique().scalars().all()
    if len(section_order.sections) != len(section_order_list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат данных")
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