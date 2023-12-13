from database.schemas import Project, Sections, Task, Comments
from sqlalchemy import insert, update, select, delete, func
from sqlalchemy.orm import joinedload, load_only, noload
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject, ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model


async def get_projects(session: AsyncSession):
    proj_qr = await session.execute(
        select(
            Project,
            func.count(Task.id).label("task_count"),
        ).options(
            load_only(
                Project.id,
                Project.is_archive,
                Project.is_favorites,
                Project.name,
            ),
            joinedload(Project.sections).load_only(
                Sections.id,
                Sections.name,
                Sections.project_id,
            ).noload(Sections.tasks),
            noload(Project.tasks),
        ).join(
            Task, isouter=True
        ).
        where(
            Task.status == 1
        ).
        group_by(
            Project
        )
    )
    
    all_proj = proj_qr.unique().all()

    project_list = my_model.ProjectList(projects=list())

    for project in all_proj:
        task_count = project[1]
        project_schema: Project = project[0]

        project_model = my_model.ProjectForList.model_validate(project_schema)
        project_model.task_count = task_count
        project_list.projects.append(project_model)

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
        order_number=task.order_number,
        comments_count=len(task.comments)
    )
    return task_object


def create_section_model(section: Sections):
    """
    Функция формирования модельки раздела с задачами
    принадлежащими этому разделу 
    """
    task_list = [create_task_model(task) for task in section.tasks]
    sorted_task = sorted(task_list, key=lambda task_model: task_model.order_number)
    
    section_object = my_model.Section(
        value=section.id,
        label=section.name,
        order_number=section.order_number,
        tasks=sorted_task
    )
    
    return section_object


async def get_project_details(project_id: int | None, session: AsyncSession):
    # получение проекта со всеми его разделами и задачами
    project_query = await session.execute(
        select(Project).
        options(
            load_only(
                Project.id,
                Project.name,
                Project.is_favorites,
            ),
            joinedload(Project.sections).
                load_only(
                    Sections.id,
                    Sections.name,
                    Sections.order_number
                ).joinedload(
                    Sections.tasks
                ).options(
                    load_only(
                        Task.id,
                        Task.name,
                        Task.status,
                        Task.description,
                        Task.order_number,
                    )
                ).joinedload(
                    Task.comments
                ).options(
                    load_only(
                        Comments.id,
                    )
                ),
        ).
        where(Project.id == project_id)
    )
    project: Project = project_query.unique().scalar_one_or_none()
    if project_id and not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    
    # получение внешних или "Входящих" задач
    external_task_query = await session.execute(
        select(
            Task.id,
            Task.name,
            Task.description,
            Task.status,
            Task.order_number,
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
 
    if project:
        section_list = [create_section_model(section) for section in project.sections]
        sorted_sections = sorted(section_list, key=lambda section_model: section_model.order_number)
        sorted_ext_task = sorted(external_tasks, key=lambda task_model: task_model.order_number)
        project_object = my_model.Project(
            id=project_id,
            name=project.name,
            is_favorites=project.is_favorites,
            tasks=sorted_ext_task,
            sections=sorted_sections
        )
    else:
        sorted_ext_task = sorted(external_tasks, key=lambda task_model: task_model.order_number)
        project_object = my_model.IncomingTasks(
            tasks=sorted_ext_task,
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