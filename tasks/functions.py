from database.schemas import Project, Sections, Task, UserInfo, Comments
from sqlalchemy import insert, update, delete, select, func
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from tasks.model import CreateTask, EditTask
from fastapi import HTTPException, status
import tasks.model as my_model
from projects.functions import check_user_project


async def get_task_list(session: AsyncSession, user: UserInfo):
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
            Task.owner == user.login
        ).
        where(
            Task.status == True
        )
    )
    task_list: list[Task] = task_query.unique().scalars().all()
    task_list_model = my_model.TaskList(task_list=list())
    for task in task_list:
        task_model = my_model.TaskForList(
            id=task.id,
            project_id=task.project_id,
            section_id=task.section_id,
            comments_count=len(task.comments),
            name=task.name,
            project_name=task.project.name,
            section_name=task.sections.name,
            to_do_date=task.to_do_date,
        )
        task_list_model.task_list.append(task_model)

    return task_list_model


async def get_task_details(task_id: int, session: AsyncSession, user: UserInfo):   
    task_query = await session.execute(
        select(Task).
        options(
            joinedload(Task.comments),
            joinedload(Task.sections).load_only(Sections.name),
            joinedload(Task.project).load_only(Project.name)
        ).
        where(Task.id == task_id).
        where(Task.owner == user.login)
    )
    task = task_query.unique().scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    
    task_model = my_model.Task.model_validate(task)
    return task_model


async def create_task(task: CreateTask, session: AsyncSession, user: UserInfo):
    task_data = task.model_dump(exclude_unset=True)
    # есть ли пользователь в проекте
    check_user = await check_user_project(task.project_id, user.id, session)
    if check_user:
        task_query = await session.execute(
            select(Sections.id, func.count(Task.id).label('task_count')).
            join(Task, isouter=True).
            where(Sections.id == task_data['section_id'])
        )
        task_number = task_query.one()
        task_data['order_number'] = task_number.task_count + 1
        
        task_data['owner'] = user.login
            
        await session.execute(insert(Task).values(task_data))
        await session.commit()


async def edit_task(task: EditTask, session: AsyncSession, user: UserInfo):
    task_query = await session.execute(select(Task.id).where(Task.id == task.id))
    task_id = task_query.scalar_one_or_none()
    if not task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    task_data = task.model_dump(exclude={'id'}, exclude_unset=True)
    # если нам передают id раздела, то id проекта мы присваиваем сами
    if task_data.get('section_id'):
        # обращаемся к указанному разделу и берем оттуда id проекта
        project_id_query = await session.execute(select(Sections.project_id).where(Sections.id == task_data['section_id']))
        project_id = project_id_query.unique().scalar_one_or_none()
        if not project_id:
            raise HTTPException(detail="Раздел не найден", status_code=status.HTTP_404_NOT_FOUND)
        if not task_data.get('order_number'):
            task_query = await session.execute(
                select(Sections.id, func.count(Task.id).label('task_count')).
                join(Task, isouter=True).
                where(Sections.id == task_data['section_id'])
            )
            task_number = task_query.one()
            task_data['order_number'] = task_number.task_count + 1
        task_data["project_id"] = project_id
    # если id раздела не передают, то нужно проверить существование переданного проекта
    # и взять оттуда id основного раздела
    elif task_data.get('project_id'):
        project_query = await session.execute(
            select(Project.id, Sections.id.label('section_id')).
            join(Sections, isouter=True).
            where(Project.id == task_data['project_id']).
            where(Sections.is_basic == True)
        )
        project = project_query.one_or_none()
        task_data['section_id'] = project.section_id
        # далее берем количество задач у проекта в основом разделе
        task_query = await session.execute(
            select(Project.id, func.count(Task.id).label('task_count')).
            join(Task, isouter=True).
            where(Project.id == task_data['project_id']).
            where(Sections.id == project.section_id)
        )
        task_number = task_query.one()
        task_data['order_number'] = task_number.task_count + 1
        # при переносе задачи в другой проект или во "Входящие", задача по умолчанию будет вне разделов
        if not project:
            raise HTTPException(detail="Проект не найден", status_code=status.HTTP_404_NOT_FOUND)
    # далее просто обновляем все данные в объекте Task и комитим
    await session.execute(
        update(Task).
        where(Task.id == task.id).
        where(Task.owner == user.login).
        values(task_data)
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
    new_order_list = list()
    # обновляем section_id у задачи, которую перетаскивают
    await session.execute(
        update(Task).
        where(Task.id == task_order.task_id).
        where(Task.owner == user.login).
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
        where(Task.owner == user.login),
        new_order_list,
        execution_options={"synchronize_session": False}
    )
    await session.commit()
    # мы исользовали "массовое обновление по первичному ключу" и из-за того, что мы 
    # добавили дополнительный "where" критерий в виде project_id, нам необходимо
    # прописать execution_options