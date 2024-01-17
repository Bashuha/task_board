from database.schemas import Project, UserInfo, ProjectUser, Task
from sqlalchemy import insert, update, select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from projects.model import ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model
from projects.functions import check_link_owner, check_user_project


async def delete_from_archive(project_id: int, session: AsyncSession, user: UserInfo):
    project_model = await check_link_owner(project_id, user.id, session)
    if project_model:
        await session.execute(
            delete(Project).
            where(Project.id == project_id).
            where(Project.is_archive == True).
            where(Project.is_incoming == False)
        )
        await session.commit()


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession, user: UserInfo):
    project_model = await check_link_owner(project.id, user.id, session)
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
    check_root = await check_link_owner(project_id, user.id, session)
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
    elif not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="пользователь не найден") 
        

async def remove_user_from_project(
    user_id: int,
    project_id: int,
    user: UserInfo,    
    session: AsyncSession,
):
    # сначала проверим, является ли пользователь админом, чтобы выполнять такие действия
    check_root = await check_link_owner(project_id, user.id, session)
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="неприемлемое действие")
    if check_root:
        # удаляем связку проект-пользователь
        await session.execute(
            delete(ProjectUser).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id == user_id)
        )
        # проверим есть ли еще пользователи в проекте помимо админа
        exist_users_query = await session.execute(
            select(ProjectUser.user_id).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id != user.id)
        )
        exist_users = exist_users_query.scalars().all()
        # если нет, то вешаем все задачи на админа (единственного пользователя)
        if not exist_users:
            new_executor = user.id
        else:
            new_executor = None
            
        await session.execute(
            update(Task).
            where(Task.executor_id == user_id).
            where(Task.project_id == project_id).
            values(executor_id=new_executor)    
        )
        await session.commit()


async def project_user_list(project_id: int, user: UserInfo, session: AsyncSession):
    await check_user_project(project_id, user.id, session)
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
    # return users
    

async def change_admin(
    project_id: int,
    user_id: int,
    is_owner: bool,
    user: UserInfo,
    session: AsyncSession,
):
    check_root = await check_link_owner(project_id, user.id, session)
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="неприемлемое действие")
    if check_root:
        await session.execute(
            update(ProjectUser).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id == user_id).
            values(is_owner=is_owner)
        )
        await session.commit()