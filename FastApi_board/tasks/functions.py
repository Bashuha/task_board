from database.schemas import Project, Sections, Task
from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from tasks.model import CreateTask, EditTask
from fastapi import HTTPException


def create_comment_dict(comment):
    comment = comment._asdict()
    comment.pop("task_id")
    return comment


async def get_task_details(task_id: int, session: AsyncSession):   
    task_qr = session.get(Task, task_id)
    task: Task = await task_qr
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    task_dict = {
        "create_date": task.create_date.strftime('%Y-%m-%d'),
        "description": task.description,
        "project_id": task.project_id,
        "project_name": "Входящие",
        "section_id": None,
        "section_name": None,
        "status": task.status,
        "id": task.id,
        "task_name": task.name,
        "task_owner": task.owner
    }

    if task.section_id:
        task_dict['section_id'] = task.Section.id
        task_dict['section_name'] = task.Section.name
        task_dict['project_name'] = task.Project.name
    elif task.project_id:
        task_dict['project_name'] = task.Project.name

    task_dict['comments'] = list(map(create_comment_dict, task.Comments))

    return task_dict


async def create_task(task: CreateTask, session: AsyncSession):
    task_data = task.model_dump(exclude={'id', 'status'})
    # если нам передали id раздела, то project_id мы подставляем сами
    if task_data.get('section_id'):
        section_qr = session.get(Sections, task_data['section_id'])
        section: Sections = await section_qr
        # если такой раздел существует, то берем оттуда project_id
        if not section:
            raise HTTPException(detail='Проект не найден', status_code=404)
        task_data["project_id"] = section.project_id
    # если передали только project_id, то мы просто проверяем его наличие
    elif task_data.get('project_id'):
        project_qr = session.get(Project, task_data['project_id'])
        project: Project = await project_qr
        if not project:
            raise HTTPException(detail='Проект не найден', status_code=404)
        
    stmt = insert(Task).values(**task_data)
    await session.execute(stmt)
    await session.commit()


async def edit_task(task: EditTask, session: AsyncSession):
    task_qr = session.get(Task, task.id)
    task_model: Task = await task_qr
    if not task_model:
        raise HTTPException(detail='Задача не найдена', status_code=404)
    task_data = task.model_dump(exclude={'id'}, exclude_unset=True)
    # если нам передают id раздела, то id проекта мы присваиваем сами
    if task_data.get('section_id'):
        # обработка идет только если section_id != None
        # в таком случае мы обращаемся к указанному разделу и берем оттуда id проекта
        section_qr = session.get(Sections, task_data['section_id'])
        section: Sections = await section_qr
        if not section:
            # если запрос вернул None, значит такого раздела в базе нет
            raise HTTPException(detail="Раздел не найден", status_code=404)
        task_data["project_id"] = section.project_id
    # если id раздела не передают, то нужно проверить существование переданного проекта
    elif task_data.get('project_id'):
        project: Project = session.get(Project, task_data['project_id'])
        # при переносе задачи в другой проект или во "Входящие", задача по умолчанию будет вне разделов
        if not project:
            raise HTTPException(detail="Проект не найден", status_code=404)
        task_data['section_id'] = None
    # далее просто обновляем все данные в объекте Task и комитим
    update_query = update(Task).where(Task.id==task.id).values(**task_data)
    await session.execute(update_query)
    await session.commit()

    return {"detail": "ok"}


async def delete_task(task_id: int, session: AsyncSession):
    task_qr = session.get(Task, task_id)
    task: Task = await task_qr
    if not task:
        raise HTTPException(detail='Задача не найдена', status_code=404)
    
    delete_query = delete(Task).where(Task.id==task_id)
    await session.execute(delete_query)
    await session.commit()