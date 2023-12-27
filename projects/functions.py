from database.schemas import Project, Sections, Task, Comments, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func, funcfilter
from sqlalchemy.orm import joinedload, load_only, noload
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject, ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model
from datetime import datetime


async def get_projects(user: UserInfo, session: AsyncSession):
    # users_project_query = await session.execute(select(ProjectUser.project_id).where(ProjectUser.user_id == user.id))

    proj_qr = await session.execute(
        select(
            Project,
            func.count(func.IF((Task.status == 1), 1, None)).label("task_count"),
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
        ).join(
            ProjectUser, isouter=True
        ).
        where(
            ProjectUser.user_id == user.id
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


async def check_user_project(project_id, session: AsyncSession, user: UserInfo):
    check_user_query = await session.execute(
        select(ProjectUser).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id == user.id)
    )
    check_user = check_user_query.one_or_none()
    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='вы не можете взаимодействовать с проектами, в которых вас нет')


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
        comments_count=len(task.comments),
        create_date=task.create_date
    )
    return task_object


def create_section_model(section: Sections):
    """
    Функция формирования модельки раздела с задачами
    принадлежащими этому разделу 
    """
    active_list = list()
    close_list = list()
    for task in section.tasks:
        model_task = create_task_model(task)
        if task.status:
            active_list.append(model_task)
        else:
            close_list.append(model_task)

    sorted_active_tasks: list[my_model.SmallTask] = sorted(active_list, key=lambda task_model: task_model.order_number)
    sorted_close_tasks: list[my_model.SmallTask] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
    
    section_object = my_model.Section(
        value=section.id,
        label=section.name,
        order_number=section.order_number,
        open_tasks=sorted_active_tasks,
        close_tasks=sorted_close_tasks,
        is_basic=section.is_basic,
    )
    
    return section_object


def create_today_task_model(task: Task):
    """
    Функия для формирования модельки задачи
    используется в get_today_tasks
    """
    task_object = my_model.TodayTask(
        id=task.id,
        name=task.name,
        description=task.description,
        status=task.status,
        project_id=task.project_id,
        project_name=task.project.name,
        section_id=task.section_id,
        section_name=task.sections.name,
        comments_count=len(task.comments),
    )
    return task_object


async def get_today_tasks(session: AsyncSession, user: UserInfo):
    today_date = datetime.today().date()
    task_query = await session.execute(
        select(Task).options(
            load_only(
                Task.id,
                Task.name,
                Task.description,
                Task.status,
                Task.project_id,
                Task.section_id,
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
            Task.to_do_date == today_date
        ).
        where(
            Task.owner == user.login
        ).
        where(
            Task.status == True
        )
    )

    today_tasks = task_query.unique().scalars().all()
    tasks_object = my_model.TodayTaskList(task_list=list())
    for task in today_tasks:
        task_model = create_today_task_model(task)
        tasks_object.task_list.append(task_model)

    return tasks_object


def create_task(task: Task):
    """
    Функия для формирования модельки задачи
    используется в project_details
    """
    task_object = my_model.TaskForDetails(
        description=task.description,
        name=task.name,
        status=task.status,
        id=task.id,
        order_number=task.order_number,
        comments_count=len(task.comments),
        create_date=task.create_date,
        section_id=task.section_id,
    )
    return task_object


async def project_details(project_id: int | None, session: AsyncSession, user: UserInfo):
    if project_id:
        await check_user_project(project_id, session, user)
        project_query = await session.execute(
            select(Project).
            options(
                load_only(
                    Project.id,
                    Project.name,
                    Project.is_favorites
                ),
                joinedload(Project.sections).
                    load_only(
                        Sections.id,
                        Sections.name,
                        Sections.order_number,
                        Sections.is_basic,
                    ),
                joinedload(Project.tasks).
                    load_only(
                        Task.id,
                        Task.name,
                        Task.status,
                        Task.description,
                        Task.order_number,
                        Task.create_date,
                        Task.section_id,
                    ).
                    joinedload(
                        Task.comments
                    ).
                    load_only(
                        Comments.id
                    )
            ).
            where(Project.id == project_id)
        )
        project: Project = project_query.unique().scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    
        active_list = list()
        close_list = list()
        for task in project.tasks:
            model_task = create_task(task)
            if task.status:
                active_list.append(model_task)
            else:
                close_list.append(model_task)
        sorted_active_tasks: list[my_model.SmallTask] = sorted(active_list, key=lambda task_model: task_model.order_number)
        sorted_close_tasks: list[my_model.SmallTask] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
        sorted_sections = sorted(project.sections, key=lambda section_model: section_model.order_number)

        project_object = my_model.ProjectDetails(
            id=project.id,
            name=project.name,
            is_favorites=project.is_favorites,
            sections=sorted_sections,
            open_tasks=sorted_active_tasks,
            close_tasks=sorted_close_tasks,
        )
    else:
        # получение "Входящих" задач
        external_task_query = await session.execute(
            select(
                Task.id,
                Task.name,
                Task.description,
                Task.status,
                Task.order_number,
                Task.create_date,
                func.count(Comments.id).label("comments_count"),
            ).
            join(Comments, isouter=True).
            where(Task.project_id == project_id).
            where(Task.owner == user.login).
            group_by(
                Task.id,
                Task.name,
                Task.description,
                Task.status,
                Task.create_date,
            )
        )
        external_tasks = external_task_query.all()
        sorted_ext_task = sorted(external_tasks, key=lambda task_model: task_model.order_number)
        project_object = my_model.IncomingTasks(
            tasks=sorted_ext_task,
        )

    return project_object


async def create_project(project: CreateProject, user: UserInfo, session: AsyncSession):
    # сначала создаем проект
    project_dict = project.model_dump()
    project_data = Project(**project_dict)
    session.add(project_data)
    await session.commit()
    # после чего создаем ему основной раздел
    section_data = my_model.SectionForCreate(project_id=project_data.id)
    section_dict = section_data.model_dump()
    session.add(Sections(**section_dict))
    await session.commit()
    await session.execute(insert(ProjectUser).values(project_id=project_data.id, user_id=user.id))
    await session.commit()


async def edit_project(project: EditProject, session: AsyncSession, user: UserInfo):
    await check_user_project(project.id, session, user)

    update_project_data = project.model_dump(exclude={'id'}, exclude_unset=True)
    update_query = update(Project).where(Project.id==project.id).values(update_project_data)
    await session.execute(update_query)
    await session.commit()


async def delete_from_archive(project_id: int, session: AsyncSession, user: UserInfo):
    await check_user_project(project_id, session, user)

    project_query = await session.execute(
        select(Project.id, Project.is_archive).
        where(Project.id == project_id)
    )
    project_model: Project = project_query.one_or_none()
    if not project_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
    
    delete_query = delete(Project).where(Project.id == project_id).where(Project.is_archive == True)
    await session.execute(delete_query)
    await session.commit()


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession, user: UserInfo):
    await check_user_project(project.id, session, user)

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