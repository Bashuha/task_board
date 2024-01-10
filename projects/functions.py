from database.schemas import Project, Sections, Task, Comments, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func
from sqlalchemy.orm import joinedload, load_only, noload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from projects.model import CreateProject, EditProject, ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model
from datetime import datetime


async def check_link(project_id: int, user_id: int, session: AsyncSession):
    project_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id == user_id).
        where(ProjectUser.is_owner == True)
    )
    project_model: Project = project_query.scalar_one_or_none()
    return project_model


async def get_projects(user: UserInfo, session: AsyncSession):

    proj_qr = await session.execute(
        select(
            Project,
            func.count(func.IF((Task.status == 1), 1, None)).label("task_count"),
            ProjectUser.is_favorites.label("is_favorites"),
        ).options(
            load_only(
                Project.id,
                Project.is_archive,
                Project.name,
                Project.is_incoming,
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
            Project.id,
            Project.is_archive,
            Project.name,
            Project.is_incoming,
            ProjectUser.is_favorites,
        )
    )
    
    all_proj = proj_qr.unique().all()

    project_list = my_model.ProjectList(projects=list())

    for project in all_proj:
        task_count = project[1]
        project_schema: Project = project[0]
        is_favorites = project[2]

        project_model = my_model.ProjectForList.model_validate(project_schema)
        project_model.task_count = task_count
        project_model.is_favorites = is_favorites
        project_list.projects.append(project_model)

    return project_list


async def check_user_project(project_id, user_id: int, session: AsyncSession):
    check_user_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id == user_id)
    )
    check_user = check_user_query.scalar_one_or_none()
    return check_user


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
            Task.to_do_date <= today_date
        ).
        where(
            Task.owner == user.login
        ).
        where(
            Task.status == True
        )
    )

    today_tasks = task_query.unique().scalars().all()
    tasks_object = my_model.TodayTaskList(today_tasks=list(), outstanding_tasks=list())
    for task in today_tasks:
        if task.to_do_date == today_date:
            task_model: my_model.TodayTask = create_today_task_model(task)
            tasks_object.today_tasks.append(task_model)
        elif task.to_do_date < today_date:
            task_model: my_model.TodayTask = create_today_task_model(task)
            tasks_object.outstanding_tasks.append(task_model)

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
        to_do_date=task.to_do_date,
    )
    return task_object


async def project_details(project_id: int | None, session: AsyncSession, user: UserInfo):
    if project_id:
        project_query = await session.execute(
            select(Project, ProjectUser.is_favorites.label('is_favorites')).
            options(
                load_only(
                    Project.id,
                    Project.name,
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
                        Task.to_do_date,
                    ).
                    joinedload(
                        Task.comments
                    ).
                    load_only(
                        Comments.id
                    )
            ).
            join(ProjectUser, isouter=True).
            where(Project.id == project_id).
            where(Project.is_incoming == False).
            where(ProjectUser.user_id == user.id)
        )
        project_info = project_query.unique().one_or_none()
        if not project_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        
        project: Project = project_info[0]
        is_favorites = project_info[1]
    
        active_list = list()
        close_list = list()
        for task in project.tasks:
            model_task = create_task(task)
            if task.status:
                active_list.append(model_task)
            else:
                close_list.append(model_task)
        sorted_active_tasks: list[my_model.TaskForDetails] = sorted(active_list, key=lambda task_model: task_model.order_number)
        sorted_close_tasks: list[my_model.TaskForDetails] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
        sorted_sections = sorted(project.sections, key=lambda section_model: section_model.order_number)
        
        me_admin = await check_link(project.id, user.id, session)

        project_object = my_model.ProjectDetails(
            id=project.id,
            name=project.name,
            is_favorites=is_favorites,
            sections=sorted_sections,
            open_tasks=sorted_active_tasks,
            close_tasks=sorted_close_tasks,
            me_admin=True if me_admin else False,
        )
    else:
        project_query = await session.execute(
            select(Project).
            options(
                load_only(
                    Project.id,
                    Project.name,
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
                        Task.to_do_date,
                    ).
                    joinedload(
                        Task.comments
                    ).
                    load_only(
                        Comments.id
                    )
            ).
            join(ProjectUser, isouter=True).
            where(Project.is_incoming == True).
            where(ProjectUser.user_id == user.id)
        )
        project = project_query.unique().scalar_one_or_none()
        active_list = list()
        close_list = list()
        for task in project.tasks:
            model_task = create_task(task)
            if task.status:
                active_list.append(model_task)
            else:
                close_list.append(model_task)

        sorted_active_tasks: list[my_model.TaskForDetails] = sorted(active_list, key=lambda task_model: task_model.order_number)
        sorted_close_tasks: list[my_model.TaskForDetails] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
        sorted_sections = sorted(project.sections, key=lambda section_model: section_model.order_number)

        project_object = my_model.ProjectDetails(
            id=project.id,
            name=project.name,
            is_favorites=False,
            sections=sorted_sections,
            open_tasks=sorted_active_tasks,
            close_tasks=sorted_close_tasks,
            me_admin=True,
        )

    return project_object


async def create_project(project: CreateProject, user: UserInfo, session: AsyncSession):
    # сначала создаем проект
    project_data = Project(name=project.name, owner=user.login)
    session.add(project_data)
    await session.commit()
    # после чего создаем ему основной раздел
    section_data = my_model.SectionForCreate(project_id=project_data.id)
    section_dict = section_data.model_dump()
    session.add(Sections(**section_dict))
    await session.commit()
    await session.execute(
        insert(ProjectUser).
        values(
            project_id=project_data.id,
            user_id=user.id,
            is_favorites=project.is_favorites,
            is_owner=True,
        )
    )
    await session.commit()
    return project_data.id


async def edit_project(project: EditProject, session: AsyncSession, user: UserInfo):

    update_project_data = project.model_dump(exclude={'id'}, exclude_unset=True)
    if update_project_data.get('is_favorites') is not None:
        await session.execute(
            update(ProjectUser).
            where(ProjectUser.user_id == user.id).
            where(ProjectUser.project_id == project.id).
            values(is_favorites=update_project_data.pop('is_favorites'))
        )
    if update_project_data:
        project_model = await check_link(project.id, user.id, session)

        if project_model:
            await session.execute(
                update(Project).
                where(Project.id == project.id).
                where(Project.is_incoming == False).
                where(Project.owner == user.login).
                values(update_project_data)
            )
    await session.commit()


async def delete_from_archive(project_id: int, session: AsyncSession, user: UserInfo):

    project_model = await check_link(project_id, user.id, session)
    if project_model:
        await session.execute(
            delete(Project).
            where(Project.id == project_id).
            where(Project.is_archive == True).
            where(Project.is_incoming == False)
        )
        await session.commit()


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession, user: UserInfo):
    project_model = await check_link(project.id, user.id, session)
    if project_model:
        await session.execute(
            update(Project).
            where(Project.id == project.id).
            where(Project.is_incoming == False).
            values(is_archive=project.is_archive)
        )
        await session.execute(
            update(ProjectUser).
            where(ProjectUser.project_id == project.id).
            values(is_favorites=False)
        )
        await session.commit()


async def add_user_to_project(
    login: str,
    project_id: int,
    session: AsyncSession,
    user: UserInfo
):
    # берем id пользователя, которого хотим добавить в проект
    user_id_query = await session.execute(
        select(UserInfo.id).
        where(UserInfo.login == login)
    )
    user_id = user_id_query.scalar_one_or_none()
    # далее проверяем есть ли такая связка в таблице
    # может ли текущий пользователь добавлять кого-то в проект
    check_root = await check_link(project_id, user.id, session)
    if user_id and check_root:
        try:
            await session.execute(
                insert(ProjectUser).
                values(
                    user_id=user_id,
                    project_id=project_id
                )
            )
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="пользователь уже в проекте")
        

async def remove_user_from_project(
    user_id: int,
    project_id: int,
    user: UserInfo,    
    session: AsyncSession,
):
    check_root = await check_link(project_id, user.id, session)
    if check_root:
        await session.execute(
            delete(ProjectUser).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id == user_id)
        )
        await session.commit()


async def project_user_list(project_id: int, user: UserInfo, session: AsyncSession):
    check_root = await check_link(project_id, user.id, session)
    if check_root:
        users_query = await session.execute(
            select(
                ProjectUser.user_id,
                ProjectUser.is_owner,
                UserInfo.first_name,
                UserInfo.second_name,
                UserInfo.login,
            ).
            join(UserInfo, UserInfo.id == ProjectUser.user_id, isouter=True).
            where(ProjectUser.project_id == project_id)
        )
        users = users_query.all()
        users_list = my_model.ProjectUserList(users_list=list())
        for user_info in users:
            user_model = my_model.ProjectUserInfo(
                user_id=user_info.user_id,
                is_owner=user_info.is_owner,
                first_name=user_info.first_name,
                second_name=user_info.second_name,
                login=user_info.login,
            )
            users_list.users_list.append(user_model)
        return users_list