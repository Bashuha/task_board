from projects.functions import check_link_owner
from sqlalchemy import insert, update, delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sections.model import CreateSection, EditSection, SectionOrder, DeleteSection
from fastapi import HTTPException, status
from database.schemas import Project, Sections, UserInfo
from sections.dao import SectionDAO


async def create_section(section: CreateSection, session: AsyncSession, user: UserInfo):
    """
    Создание раздела
    """
    check_root = await check_link_owner(section.project_id, user.id, session)
    if check_root:
        project_query = await session.execute(
            select(Project.id, func.count(Sections.id).label("section_count")).
            join(Sections, isouter=True).
            where(Project.id == section.project_id)
        )
        project = project_query.one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='проект не найден')
        
        section_data = section.model_dump()
        section_data['order_number'] = project.section_count + 1
        await SectionDAO.insert_data(
            session=session,
            data=section_data,
        )


async def edit_section(section: EditSection, session: AsyncSession, user: UserInfo):
    """
    Редактирование раздела
    """
    check_root = await check_link_owner(section.project_id, user.id, session)
    if check_root:
        section_data = section.model_dump(exclude={'id'})
        await SectionDAO.update_data(
            session=session,
            filters={
                "id": section.id,
                "is_basic": False,
            },
            values=section_data,
        )


async def delete_section(section: DeleteSection, session: AsyncSession, user: UserInfo):
    """
    Удаление раздела
    """
    check_root = await check_link_owner(section.project_id, user.id, session)
    if check_root:
        await SectionDAO.delete_data(
            session=session,
            filters={
                "id": section.id,
                "is_basic": False,
            }
        )


async def change_section_order(section_order: SectionOrder, session: AsyncSession, user: UserInfo):
    """
    Изменение порядка разделов
    """
    check_root = await check_link_owner(section_order.project_id, user.id, session)
    if check_root:
        new_order_list = list()
        sections_qr = select(Sections).where(Sections.project_id == section_order.project_id).order_by(Sections.order_number)
        section_list_model = await session.execute(sections_qr)
        section_order_list = section_list_model.unique().scalars().all()

        if len(section_order_list) != len(section_order.sections):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="количество разделов не совпадвет")
        if section_order.sections[0].id != section_order_list[0].id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="основной раздел всегда должен быть первый")
        # создаем словарь из нового списка id и генерируем новый порядковый номер
        for number, sec_id in enumerate(section_order.sections, start=1):
            order_dict = {"id": sec_id.id, "order_number": number}
            # добавляем полученный словарь в список для UPDATE
            new_order_list.append(order_dict)
        # одним запросом обновляем порядок, используя наш список словарей
        await session.execute(
            update(Sections).
            where(Sections.project_id==section_order.project_id),
            new_order_list,
            execution_options={"synchronize_session": False}
        )
        await session.commit()
        # мы исользовали "массовое обновление по первичному ключу" и из-за того, что мы 
        # добавили дополнительный "where" критерий в виде project_id, нам необходимо
        # прописать execution_options