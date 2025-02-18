from database.schemas import Project, Sections, Task, Comments, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func, or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from projects.model import CreateProject, EditProject
from fastapi import status, HTTPException
import projects.model as my_model
from datetime import datetime
from projects.dao import ProjectDAO, ProjectUserDAO
from sections.dao import SectionDAO
from tasks.dao import TaskDAO


async def check_link_owner(project_id: int, user_id: int, session: AsyncSession):
    """
    Проврка, является ли пользователь админом проекта
    """
    project_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id == user_id).
        where(ProjectUser.is_owner == True)
    )
    project_id_from_db = project_query.scalar_one_or_none()
    return project_id_from_db


async def get_projects(user: UserInfo, session: AsyncSession):
    """
    Получить все свои проекты
    """
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
                Sections.is_basic,
            ).noload(Sections.tasks),
            joinedload(Project.user_link).load_only(ProjectUser.user_id)
        ).join(
            Task, isouter=True
        ).
        join(
            ProjectUser, isouter=True
        ).
        where(
            ProjectUser.user_id == user.id,
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
        project_model = my_model.ProjectForList.model_validate(project.Project)
        project_model.task_count = project.task_count
        project_model.is_favorites = project.is_favorites
        project_list.projects.append(project_model)

    return project_list


async def check_user_project(project_id: int, user_id: int, session: AsyncSession):
    """
    Функция проверяет, может ли пользователь взаимодействовать с проектом
    """
    check_user_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id == user_id)
    )
    check_user = check_user_query.scalar_one_or_none()
    if not check_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='нет доступа к проекту')


async def get_today_tasks(session: AsyncSession, user: UserInfo):
    """
    Получить свои сегодняшние задачи
    """
    today_date = datetime.today().date()
    project_ids_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.user_id == user.id)
    )
    project_ids = project_ids_query.scalars().all()
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
                ),
            joinedload(Task.tag_info),
        ).
        where(
            Task.to_do_date <= today_date,
            Task.status == True
        ).
        where(
            or_(Task.executor_id == user.id, Task.executor_id == None)
        ).
        where(
            Task.project_id.in_(project_ids)
        )
    )

    today_tasks = task_query.unique().scalars().all()
    outstanding_tasks = list()
    today_tasks_list = list()
    for task in today_tasks:
        if task.to_do_date == today_date:
            today_tasks_list.append(task)
        elif task.to_do_date < today_date:
            outstanding_tasks.append(task)
    tasks_object = my_model.TodayTaskList(
        today_tasks=today_tasks_list,
        outstanding_tasks=outstanding_tasks
    )

    return tasks_object


async def project_details(project_id: int | None, session: AsyncSession, user: UserInfo):
    """
    Получить детализацию проекта по его id
    или получить "Входящие" задачи, если id проекта не был указан
    """
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
                    joinedload(
                        Task.comments
                    ).
                    load_only(
                        Comments.id
                    ),
                joinedload(Project.user_link).load_only(ProjectUser.user_id),
                joinedload(Project.tasks).
                    joinedload(Task.executor_info),
                joinedload(Project.tasks).
                    joinedload(Task.owner_info),
                joinedload(Project.tasks).
                    joinedload(Task.task_giver_info),
                joinedload(Project.tasks).
                    joinedload(Task.tag_info),
            ).
            join(ProjectUser, isouter=True).
            where(Project.id == project_id).
            where(Project.is_incoming == False).
            where(Project.is_archive == False).
            where(ProjectUser.user_id == user.id)
        )
        project_info: Project = project_query.unique().one_or_none()
        if not project_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="проект не найден")
        
        active_list = list()
        close_list = list()
        for task in project_info.Project.tasks:
            if task.status:
                active_list.append(task)
            else:
                close_list.append(task)
        sorted_active_tasks: list[my_model.TaskForDetails] = sorted(active_list, key=lambda task_model: task_model.order_number)
        sorted_close_tasks: list[my_model.TaskForDetails] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
        sorted_sections = sorted(project_info.Project.sections, key=lambda section_model: section_model.order_number)
        
        me_admin = await check_link_owner(project_info.Project.id, user.id, session)

        project_object = my_model.ProjectDetails(
            id=project_info.Project.id,
            name=project_info.Project.name,
            is_favorites=project_info.is_favorites,
            sections=sorted_sections,
            open_tasks=sorted_active_tasks,
            close_tasks=sorted_close_tasks,
            me_admin=True if me_admin else False,
            users_count=len(project_info.Project.user_link)
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
                    ),
                joinedload(Project.tasks).
                    joinedload(Task.executor_info),
                joinedload(Project.tasks).
                    joinedload(Task.owner_info),
                joinedload(Project.tasks).
                    joinedload(Task.task_giver_info),
                joinedload(Project.user_link).load_only(ProjectUser.user_id),
                joinedload(Project.tasks).
                    joinedload(Task.tag_info),
            ).
            join(ProjectUser, isouter=True).
            where(Project.is_incoming == True).
            where(ProjectUser.user_id == user.id)
        )
        project_info = project_query.unique().scalar_one_or_none()
        active_list = list()
        close_list = list()
        for task in project_info.tasks:
            if task.status:
                active_list.append(task)
            else:
                close_list.append(task)

        sorted_active_tasks: list[my_model.TaskForDetails] = sorted(active_list, key=lambda task_model: task_model.order_number)
        sorted_close_tasks: list[my_model.TaskForDetails] = sorted(close_list, key=lambda task_model: task_model.create_date, reverse=True)
        sorted_sections = sorted(project_info.sections, key=lambda section_model: section_model.order_number)

        project_object = my_model.ProjectDetails(
            id=project_info.id,
            name=project_info.name,
            is_favorites=False,
            sections=sorted_sections,
            open_tasks=sorted_active_tasks,
            close_tasks=sorted_close_tasks,
            me_admin=True,
            users_count=len(project_info.user_link),
        )

    return project_object


async def create_project(project_data: CreateProject, user_id: int, session: AsyncSession):
    """
    Создание проекта и основного раздела для него
    """
    # сначала создаем проект
    project_id = await ProjectDAO.insert_data(
        session=session,
        data=project_data.model_dump(exclude={'is_favorites'})
    )
    # после чего создаем ему основной раздел
    section_data = my_model.SectionForCreate(project_id=project_id)
    await SectionDAO.insert_data(
        session=session,
        data=section_data.model_dump()
    )
    # потом создаем связь пользователя и проекта
    project_user_dict = {
        "project_id": project_id,
        "user_id": user_id,
        "is_favorites": project_data.is_favorites,
        "is_owner": True,
    }
    await ProjectUserDAO.insert_data(
        session=session,
        data=project_user_dict
    )
    return project_id


async def edit_project(project: EditProject, session: AsyncSession, user: UserInfo):
    """
    Редактирование проекта, менять проект может только админ
    однако добавлять у себя в избранное может каждый пользователь в проекте
    """
    update_project_data = project.model_dump(exclude={'id'}, exclude_unset=True)
    if update_project_data.get('is_favorites') is not None:
        await ProjectUserDAO.update_data(
            session=session,
            filters={
                "user_id": user.id,
                "project_id": project.id
            },
            values={
                "is_favorites": update_project_data.pop("is_favorites")
            }
        )
    if update_project_data:
        check_root = await check_link_owner(project.id, user.id, session)

        if check_root:
            await ProjectDAO.update_data(
                session=session,
                filters={
                    "id": project.id,
                    "is_incoming": False
                },
                values=update_project_data
            )


async def exit_project(project_id: int, session: AsyncSession, user: UserInfo):
    """
    Выход пользователя из проекта
    и передача админских прав если из проекта уходит админ.
    Передача админских прав происходит в том случае,
    если после нашего выхода, админов в проекте не осталось
    """
    # для начала проверим, является ли пользователь админом
    check_root = await check_link_owner(project_id, user.id, session)
    del_trigger = True
    # потом проверим есть ли в проекте админы помимо него
    check_admin_query = await session.execute(
        select(ProjectUser.user_id).
        where(ProjectUser.project_id == project_id).
        where(ProjectUser.user_id != user.id).
        where(ProjectUser.is_owner == True)
    )
    admin_id = check_admin_query.scalar()
    # если он админ и других админов в проекте нет, мы начинаем заниматься передачей прав админа
    if check_root and not admin_id:
        exist_users_query = await session.execute(
            select(ProjectUser.user_id).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id != user.id)
        )
        exist_users = exist_users_query.scalars().all()
        # если там пользователи еще есть, то отдаем права админа первому в списке
        if exist_users:
            new_admin_id = exist_users[0]
            await ProjectUserDAO.update_data(
                session=session,
                filters={
                    "project_id": project_id,
                    "user_id": new_admin_id,
                },
                values={"is_owner": True}
            )
            # если остался всего один пользователь, то вешаем на него все задачи проекта
            if len(exist_users) == 1:
                await TaskDAO.update_data(
                    session=session,
                    filters={"project_id": project_id},
                    values={"executor_id": new_admin_id}
                )
            # в противном случае везде, где он был исполнитель теперь будет NULL
            else:
                await TaskDAO.update_data(
                    session=session,
                    filters={
                        "project_id": project_id,
                        "executor_id": user.id,
                    },
                    values={"executor_id": None}
                )
        # ну а если больше пользователей не осталось, то мы удаляем проект
        else:
            await ProjectDAO.delete_data(
                session=session,
                filters={"id": project_id}
            )
            del_trigger = False
    # если проект еще не удалился, то мы удаляем связь пользователя и проекта
    if del_trigger:
        await ProjectUserDAO.delete_data(
            session=session,
            filters={
                "project_id": project_id,
                "user_id": user.id,
            }
        )