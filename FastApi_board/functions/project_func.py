from models import Project, Sections, Task
from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from  type_model import Project as PydanticProject
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


async def get_project_details(project_id: int, session: AsyncSession):

    project_task = session.get(Project, project_id)
    project: Project = await project_task
    if project_id != None and not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # создаем словарь, который отдадим на фронт
    project_dict = {
        "id": project_id,
        "name": "Входящие",
        "tasks": list()
    }
    # если передали project_id, то мы добавляем ключи в итоговый словарь
    # затем идем по его разделам, и формируем из них словари   
    section_dict = dict()
    if project:
        project_dict["is_favorites"] = project.is_favorites
        project_dict['name'] = project.name
    
        for section in project.Sections:
            section: Sections
            section_dict[section.id] = {
                "id": section.id,
                "name": section.name,
                "tasks": list()
            }
    task_list_qr = await session.execute(select(Task).where(Task.project_id==project_id))
    task_list = task_list_qr.scalars().all()
    # берем задачи из этого проекта (или задачи вне всех проектов)
    # идем по этим задачам, создаем нужный словарь
    for task in task_list:
        task: Task
        task_dict = {
            "description": task.description,
            "name": task.name,
            "status": task.status,
            "id": task.id,
            "comments_count": len(task.Comments)
        }
        # если находим задачу с разделом, то добавляем ее в словарь разделов
        # в противном случае просто добавляем задачу в проект вне разделов 
        if task.section_id:
            section_dict[task.section_id]['tasks'].append(task_dict)
        else:
            project_dict['tasks'].append(task_dict)
    # если передавали project_id, мы добавляем ключ в итоговый словарь со списком разделов
    if project:
        project_dict['sections'] = list(section_dict.values())

    return project_dict


async def create_project(project: PydanticProject, session: AsyncSession):
    stmt = insert(Project).values(project.model_dump(include={'name', 'is_favorites'}))
    await session.execute(stmt)
    await session.commit()


async def edit_project(project: PydanticProject, session: AsyncSession):
    project_qr = session.get(Project, project.id)
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(status_code=404, detail="Проект не найден")

    update_project_data = project.model_dump(include={'name', 'is_favorites'})
    update_query = update(Project).where(Project.id==project.id).values(**update_project_data)
    await session.execute(update_query)
    await session.commit()

    return {"message": "ok"}


async def delete_from_archive(project_id: int, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(detail="Проект не найден", status_code=404)
    if not project_model.is_archive:
        raise HTTPException(detail="Проект не в архиве", status_code=400)
    
    delete_query = delete(Project).where(Project.id==project_id)
    await session.execute(delete_query)
    await session.commit()
    return {"message": "Проект удален"}


async def change_archive_status(project: PydanticProject, session: AsyncSession):
    project = project.model_dump(exclude={'name'})
    project_qr = session.get(Project, project['id'])
    project_model: Project = await project_qr
    if not project_model:
        raise HTTPException(detail="Проект не найден", status_code=404)
    project_model.is_archive = project['is_archive']
    await session.commit()