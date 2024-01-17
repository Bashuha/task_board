from database.schemas import Project, Sections, Task, UserInfo, Comments, ProjectUser
from sqlalchemy import insert, update, delete, select, func, or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from tasks.model import CreateTask, EditTask
from fastapi import HTTPException, status
import tasks.model as my_model
from projects.functions import check_user_project


async def get_task_list(session: AsyncSession, user: UserInfo):
    project_ids_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.user_id == user.id)
    )
    project_ids = project_ids_query.scalars().all()
    task_query = await session.execute(
        select(Task).options(
            load_only(
                Task.id,
                Task.name,
                Task.description,
                Task.project_id,
                Task.section_id,
                Task.to_do_date,
            ),
            joinedload(Task.project).
                load_only(
                    Project.name
                ),
            joinedload(Task.sections).
                load_only(
                    Sections.name
                ),
            joinedload(Task.comments).
                load_only(
                    Comments.id
                )
        ).
        where(
            or_(Task.executor_id == user.id, Task.executor_id == None)
        ).
        where(
            Task.status == True
        ).
        where(
            Task.project_id.in_(project_ids)
        )
    )
    task_list: list[Task] = task_query.unique().scalars().all()
    task_list_object = my_model.TaskList(task_list=task_list)

    return task_list_object


async def get_task_details(task_id: int, session: AsyncSession, user: UserInfo):  
    task_query = await session.execute(
        select(Task).
        options(
            joinedload(Task.comments),
            joinedload(Task.sections).load_only(Sections.name),
            joinedload(Task.project).load_only(Project.name),
            joinedload(Task.executor_info),
            joinedload(Task.owner_info),
            joinedload(Task.task_giver_info)
        ).
        where(Task.id == task_id)
    )
    task = task_query.unique().scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='задача не найдена')
    await check_user_project(task.project_id, user.id, session)
    return task


async def create_task(task: CreateTask, session: AsyncSession, user: UserInfo):
    # есть ли пользователь в проекте
    task_query = await session.execute(
        select(Sections.id, Sections.project_id, func.count(Task.order_number).label('task_count')).
        join(Task, isouter=True).
        # where(Task.status == True).
        where(Sections.id == task.section_id)
    )
    task_info = task_query.one()
    await check_user_project(task_info.project_id, user.id, session)
    if task.executor_id:
        await check_user_project(task_info.project_id, task.executor_id, session)
    
    task_data = task.model_dump(exclude_unset=True)
    task_data['order_number'] = task_info.task_count + 1
    task_data['owner_id'] = user.id
    task_data['project_id'] = task_info.project_id
        
    await session.execute(insert(Task).values(task_data))
    await session.commit()


async def edit_task(task: EditTask, session: AsyncSession, user: UserInfo):
    task_query = await session.execute(select(Task.project_id).where(Task.id == task.id))
    project_id = task_query.scalar_one_or_none()
    if not project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='задача не найдена')
    await check_user_project(project_id, user.id, session)

    task_data = task.model_dump(exclude={'id'}, exclude_unset=True)
    if task.executor_id:
        await check_user_project(project_id, task.executor_id, session)
        task_data['task_giver_id'] = user.id

    # если нам передают id раздела, то id проекта мы присваиваем сами
    if task_data.get('section_id'):
        # обращаемся к указанному разделу и берем оттуда id проекта и пеезаписываем project_id
        project_id_query = await session.execute(select(Sections.project_id).where(Sections.id == task_data['section_id']))
        project_id = project_id_query.unique().scalar_one_or_none()

        if not project_id:
            raise HTTPException(detail="раздел не найден", status_code=status.HTTP_404_NOT_FOUND)
        await check_user_project(project_id, user.id, session)
        
        task_query = await session.execute(
            select(Sections.id, func.count(Task.id).label('task_count')).
            join(Task, isouter=True).
            where(Task.status == True).
            where(Sections.id == task_data['section_id'])
        )
        task_number = task_query.one()
        task_data['order_number'] = task_number.task_count + 1
        task_data["project_id"] = project_id
    # далее просто обновляем все данные в объекте Task и комитим
    await session.execute(
        update(Task).
        where(Task.id == task.id).
        values(task_data)
    )
    await session.commit()


async def change_task_status(
    change_status: my_model.ChangeTaskStatus,
    user: UserInfo,
    session: AsyncSession
):
    await check_user_project(change_status.project_id, user.id, session)
    change_dict = {'status': change_status.status}
    if change_status.status:
        task_query = await session.execute(
            select(Sections.id, func.MAX(Task.order_number).label('task_count')).
            join(Task, isouter=True).
            where(Task.status == True).
            where(Sections.id == change_status.section_id)
        )
        task_number = task_query.one()
        change_dict['order_number'] = task_number.task_count + 1
    await session.execute(
        update(Task).
        where(Task.id == change_status.id).
        where(Task.project_id == change_status.project_id).
        where(Task.section_id == change_status.section_id).
        values(change_dict)
    )
    await session.commit()


async def delete_task(task_id: int, session: AsyncSession, user: UserInfo):
    task_query = await session.execute(select(Task.id).where(Task.id == task_id))
    task = task_query.scalar_one_or_none()
    if not task:
        raise HTTPException(detail='Задача не найдена', status_code=status.HTTP_404_NOT_FOUND)
    
    delete_query = delete(Task).where(Task.id == task_id).where(Task.owner == user.login)
    await session.execute(delete_query)
    await session.commit()


async def change_task_order(task_order: my_model.TaskOrder, session: AsyncSession, user: UserInfo):
    await check_user_project(task_order.project_id, user.id, session)
    new_order_list = list()
    # обновляем section_id у задачи, которую перетаскивают
    await session.execute(
        update(Task).
        where(Task.id == task_order.task_id).
        values(section_id = task_order.section_id))
    await session.commit()
    # создаем словарь из нового списка id и генерируем новый порядковый номер
    for number, task_id in enumerate(task_order.tasks, start=1):
        order_dict = {"id": task_id.id, "order_number": number}
        # добавляем полученный словарь в список для UPDATE
        new_order_list.append(order_dict)
    # одним запросом обновляем порядок, используя наш список словарей
    await session.execute(
        update(Task).
        where(Task.section_id == task_order.section_id).
        where(Task.project_id == task_order.project_id),
        new_order_list,
        execution_options={"synchronize_session": False}
    )
    await session.commit()
    # мы исользовали "массовое обновление по первичному ключу" и из-за того, что мы 
    # добавили дополнительный "where" критерий в виде project_id, нам необходимо
    # прописать execution_options