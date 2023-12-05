from database.schemas import Project, Sections, Task, Comments
from sqlalchemy import insert, update, select, delete, func
from sqlalchemy.orm import load_only, noload
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject, ChangeArchiveStatus
from fastapi import status, HTTPException


async def get_projects(session: AsyncSession):
    projects = await session.execute(select(Project))
    project_list = {"projects": list()}
    projects_data = projects.unique().scalars().all()
    for project in projects_data:

        project_dict = {
            "label": project.name,
            "is_favorites": project.is_favorites,
            "is_archive": project.is_archive,
            "value": project.id,
            "task_count": len([i.status for i in project.Task if i.status == 1]),
            "sections": list()
        }
        for section in project.Sections:
            section_dict = {
                "value": section.id,
                "label": section.name,
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
        "name": section.name,
        "order_num": section.order_number
    }
    section_dict['tasks'] = list(map(create_task_dict, section.Task))
    
    return section_dict


async def get_project_details(project_id: int, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project: Project = await project_qr
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    
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
        section_list = list(map(create_section_dict, project.Sections))
        project_dict['sections'] = sorted(section_list, key=lambda section_dict: section_dict['order_num'])

    # также формируем словарики для задач вне разделов или "Входящих" задач
    project_dict['tasks'] = list(map(create_task_dict, external_task_list))

    return project_dict


async def create_project(project: CreateProject, session: AsyncSession):
    stmt = insert(Project).values(project.model_dump())
    await session.execute(stmt)
    await session.commit()


async def edit_project(project: EditProject, session: AsyncSession):
    update_project_data = project.model_dump(exclude={'id'}, exclude_unset=True)
    update_query = update(Project).where(Project.id==project.id).values(update_project_data)
    await session.execute(update_query)
    await session.commit()


async def delete_from_archive(project_id: int, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    if not project_model.is_archive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Проект не в архиве")
    
    delete_query = delete(Project).where(Project.id==project_id)
    await session.execute(delete_query)
    await session.commit()


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession):
    project_qr = session.get(Project, project.id)
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    project_model.is_archive = project.is_archive
    if project.is_archive:
        project_model.is_favorites = False
    await session.commit()