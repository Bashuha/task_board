from database.schemas import Project, Sections, Task
from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject, ChangeArchiveStatus, NotFoundError
from fastapi.responses import JSONResponse
from fastapi import HTTPException


async def get_projects(session: AsyncSession):
    projects = await session.execute(select(Project))
    project_list = {"projects": list()}
    projects_data = projects.scalars().all()
    for project in projects_data:

        project_dict = {
            "project_name": project.name,
            "is_favorites": project.is_favorites,
            "is_archive": project.is_archive,
            "id": project.id,
            "task_count": len(project.Task),
            "sections": list()
        }
        for section in project.Sections:
            section_dict = {
                "id": section.id,
                "name": section.name,
                "project_id": section.project_id
            }
            project_dict['sections'].append(section_dict)
        
        project_list['projects'].append(project_dict)

    return project_list


def create_task_dict(task: Task):
    """
    Функия для формирования словаря задачи
    используется в get_project_details и в create_section_dict
    """
    task_dict = {
        "description": task.description,
        "name": task.name,
        "status": task.status,
        "id": task.id,
        "comments_count": len(task.Comments)
    }
    return task_dict


def create_section_dict(section: Sections):
    """
    Функция формирования словаря раздела с задачами
    принадлежащими этому разделу 
    """
    section_dict = {
        "id": section.id,
        "name": section.name
    }
    section_dict['tasks'] = list(map(create_task_dict, section.Task))
    
    return section_dict


async def get_project_details(project_id: int, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project: Project = await project_qr
    if project_id != None and not project:
        return JSONResponse(status_code=404, content={"message": "Проект не найден"})
    
    # делаем запрос на получение задач вне разделов (это могут быть и "Входящие" задачи)
    external_task_qr = select(Task).where(Task.section_id == None, Task.project_id == project_id)
    external_task = await session.execute(external_task_qr)
    external_task_list = external_task.scalars().all()
    # создаем словарь, который отдадим на фронт
    project_dict = {
        "id": project_id,
        "name": "Входящие"
    }
    # если передали project_id, то мы добавляем ключи в итоговый словарь
    # затем идем по его разделам, и формируем из них словари   
    if project:
        project_dict["is_favorites"] = project.is_favorites
        project_dict['name'] = project.name
        project_dict['sections'] = list(map(create_section_dict, project.Sections))

    # также формируем словарики для задач вне разделов или "Входящих" задач
    project_dict['tasks'] = list(map(create_task_dict, external_task_list))

    return project_dict


async def create_project(project: CreateProject, session: AsyncSession):
    stmt = insert(Project).values(project.model_dump())
    await session.execute(stmt)
    await session.commit()


async def edit_project(project: EditProject, session: AsyncSession):
    project_qr = session.get(Project, project.id)
    project_model: Project = await project_qr
    if not project_model:
        return JSONResponse(status_code=404, content={"message": "Проект не найден"})

    update_project_data = project.model_dump(exclude={'id'}, exclude_unset=True)
    update_query = update(Project).where(Project.id==project.id).values(update_project_data)
    await session.execute(update_query)
    await session.commit()

    return {"message": "ok"}


async def delete_from_archive(project_id: int, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project_model: Project = await project_qr
    if not project_model:
        return JSONResponse(status_code=404, content={"message": "Проект не найден"})
    if not project_model.is_archive:
        raise HTTPException(detail="Проект не в архиве", status_code=400)
    
    delete_query = delete(Project).where(Project.id==project_id)
    await session.execute(delete_query)
    await session.commit()
    return {"message": "Проект удален"}


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession):
    project = project.model_dump(exclude={'name'})
    project_qr = session.get(Project, project['id'])
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(detail="Проект не найден", status_code=404)
    project_model.is_archive = project['is_archive']
    await session.commit()