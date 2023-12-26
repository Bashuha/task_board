from database.schemas import Project, Sections, Task, UserInfo
from sqlalchemy import insert, update, delete, select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from tasks.model import CreateTask, EditTask
from fastapi import HTTPException, status
import tasks.model as my_model


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

    if task.section_id:
        task_model.section_name = task.sections.name
        task_model.project_name = task.project.name
    elif task.project_id:
        task_model.project_name = task.project.name

    return task_model


async def create_task(task: CreateTask, session: AsyncSession, user: UserInfo):
    task_data = task.model_dump(exclude_unset=True)
    # если нам передали id раздела, то project_id мы подставляем сами
    if task_data.get('section_id'):
        project_id_query = await session.execute(select(Sections.project_id).where(Sections.id == task_data['section_id']))
        project_id: Sections = project_id_query.scalar_one_or_none()
        # если такой раздел существует, то берем оттуда project_id
        if not project_id:
            raise HTTPException(detail='Проект не найден', status_code=status.HTTP_404_NOT_FOUND)
        task_data["project_id"] = project_id
        task_query = await session.execute(
            select(Sections.id, func.count(Task.id).label('task_count')).
            join(Task, isouter=True).
            where(Sections.id == task_data['section_id'])
        )
        task_number = task_query.one()
        task_data['order_number'] = task_number.task_count + 1
        
    # если передали только project_id, то мы просто проверяем его наличие
    elif task_data.get('project_id'):
        # заодно берем id основного раздела
        project_query = await session.execute(
            select(Project.id, Sections.id.label('section_id')).
            join(Sections, isouter=True).
            where(Project.id == task_data['project_id']).
            where(Sections.is_basic == True)
        )
        project: Project = project_query.one_or_none()
        if not project:
            raise HTTPException(detail='Проект не найден', status_code=status.HTTP_404_NOT_FOUND)
        # далее берем количество задач у проекта в основом разделе
        task_query = await session.execute(
            select(Project.id, func.count(Task.id).label('task_count')).
            join(Task, isouter=True).
            where(Project.id == task_data['project_id']).
            where(Sections.id == project.section_id)
        )
        task_data['section_id'] = project.section_id
        task_number = task_query.one()
        task_data['order_number'] = task_number.task_count + 1
    else:
        task_query = await session.execute(
            select(func.count(Task.id).label('task_count')).
            where(Task.project_id == None)
        )
        task_number = task_query.scalar_one()
        task_data['order_number'] = task_number + 1
        
    task_data['owner'] = user.login
        
    stmt = insert(Task).values(task_data)
    await session.execute(stmt)
    await session.commit()


async def check_task_user(task_id: int, session: AsyncSession, user: UserInfo):
    check_user_query = await session.execute(
        select(Task.id).
        where(Task.id == task_id).
        where(Task.owner == user.login)
    )
    check_user = check_user_query.one_or_none()
    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='вы не можете взаимодействовать с этими задачами')


async def edit_task(task: EditTask, session: AsyncSession, user: UserInfo):
    await check_task_user(task.id, session, user)

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
    elif task_data.get('project_id'):
        project_query = await session.execute(select(Project.id).where(Project.id == task_data['project_id']))
        project = project_query.scalar_one_or_none()
        # при переносе задачи в другой проект или во "Входящие", задача по умолчанию будет вне разделов
        if not project:
            raise HTTPException(detail="Проект не найден", status_code=status.HTTP_404_NOT_FOUND)
        task_data['section_id'] = None
    # далее просто обновляем все данные в объекте Task и комитим
    update_query = update(Task).where(Task.id == task.id).values(task_data)
    await session.execute(update_query)
    await session.commit()


async def delete_task(task_id: int, session: AsyncSession, user):
    await check_task_user(task_id, session, user)

    task_query = await session.execute(select(Task.id).where(Task.id == task_id))
    task = task_query.scalar_one_or_none()
    if not task:
        raise HTTPException(detail='Задача не найдена', status_code=status.HTTP_404_NOT_FOUND)
    
    delete_query = delete(Task).where(Task.id==task_id)
    await session.execute(delete_query)
    await session.commit()


async def change_task_order(task_order: my_model.TaskOrder, session: AsyncSession, user: UserInfo):
    new_order_list = list()
    # обновляем section_id у задачи, которую перетаскивают
    await session.execute(update(Task).where(Task.id == task_order.task_id).values(section_id = task_order.section_id))
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