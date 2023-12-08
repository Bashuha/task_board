from database.schemas import Project, Sections, Task, Comments
from sqlalchemy import insert, update, select, delete, func, text
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject, ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model


async def get_projects(session: AsyncSession):
    projects = await session.execute(select(Project))
    project_list = {"projects": list()}
    projects_data = projects.unique().scalars().all()

    # proj_qr = await session.execute(
    #     select(
    #         Project.id,
    #         Project.is_archive,
    #         Project.is_favorites,
    #         Sections.id,
    #         Sections.name
    #     ).options(joinedload(Sections))
    # )
    # all_proj = proj_qr.all()

    for project in projects_data:

        project_dict = {
            "label": project.name,
            "is_favorites": project.is_favorites,
            "is_archive": project.is_archive,
            "value": project.id,
            "task_count": len([i.status for i in project.tasks if i.status == 1]),
            "sections": list()
        }
        for section in project.sections:
            section_dict = {
                "value": section.id,
                "label": section.name,
                "project_id": section.project_id
            }
            project_dict['sections'].append(section_dict)
        
        project_list['projects'].append(project_dict)

    return project_list


def create_task_model(task: Task):
    """
    Функия для формирования модельки задачи
    используется в get_project_details и в create_section_model
    """
    task_object = my_model.SmallTask(
        description=task.description,
        name=task.name,
        status=task.status,
        id=task.id,
        comments_count=len(task.comments)
    )
    return task_object


def create_section_model(section: Sections):
    """
    Функция формирования модельки раздела с задачами
    принадлежащими этому разделу 
    """
    task_list = [create_task_model(task) for task in section.tasks]
    
    section_object = my_model.Section(
        value=section.id,
        label=section.name,
        order_number=section.order_number,
        tasks=task_list
    )
    
    return section_object


async def get_project_details(project_id: int | None, session: AsyncSession):
    project_qr = session.get(Project, project_id)
    project: Project = await project_qr
    if project_id and not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
 
    if project:
        section_list = [create_section_model(section) for section in project.sections]
        sorted_sections = sorted(section_list, key=lambda section_model: section_model.order_number)

        external_tasks = list()
        for ext_task in project.tasks:
            if not ext_task.section_id:
                external_tasks.append(ext_task)
        ext_task_list = [create_task_model(task) for task in external_tasks]
        project_object = my_model.Project(
            id=project_id,
            name=project.name,
            is_favorites=project.is_favorites,
            tasks=ext_task_list,
            sections=sorted_sections
        )
    else:
        # если project_id не передали, делаем запрос на входящие задачи
        external_task_query = await session.execute(
            select(
                Task.id,
                Task.name,
                Task.description,
                Task.status,
                func.count(Comments.id).label("comments_count")
            ).
            join(Comments, isouter=True).
            where(Task.project_id == project_id).
            group_by(
                Task.id,
                Task.name,
                Task.description,
                Task.status
            )
        )
        external_tasks = external_task_query.all()
        project_object = my_model.IncomingTasks(
            tasks=external_tasks,
        )

    return project_object


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
    project_query = await session.execute(
        select(Project.id, Project.is_archive).
        where(Project.id == project_id)
    )
    project_model: Project = project_query.one_or_none()
    if not project_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    if not project_model.is_archive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Проект не в архиве")
    
    delete_query = delete(Project).where(Project.id==project_id)
    await session.execute(delete_query)
    await session.commit()


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession):
    project_query = await session.execute(select(Project.id).where(Project.id == project.id))
    project_id = project_query.scalar_one_or_none()
    if not project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    await session.execute(
        update(Project).
        where(Project.id == project.id).
        values(is_archive=project.is_archive, is_favorites=False)
    )
    await session.commit()