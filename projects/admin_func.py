from database.schemas import Project, UserInfo, ProjectUser, Task
from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from projects.model import ChangeArchiveStatus
from fastapi import status, HTTPException
import projects.model as my_model
from projects.functions import check_link_owner, check_user_project
from projects.dao import ProjectUserDAO, ProjectDAO
from tasks.dao import TaskDAO


async def delete_from_archive(project_id: int, session: AsyncSession, user: UserInfo):
    """
    Удалить проект из архива
    """
    project_model = await check_link_owner(project_id, user.id, session)
    if project_model:
        await ProjectDAO.delete_data(
            session=session,
            filters={
                "id": project_id,
                "is_archive": True,
                "is_incoming": False,
            }
        )


async def change_archive_status(project: ChangeArchiveStatus, session: AsyncSession, user: UserInfo):
    """
    Переместить проект в архив или достать из архива
    """
    project_model = await check_link_owner(project.id, user.id, session)
    if project_model:
        await ProjectDAO.update_data(
            session=session,
            filters={
                "id": project.id,
                "is_incoming": False,
            },
            values={'is_archive': project.is_archive}
        )
        await ProjectUserDAO.update_data(
            session=session,
            filters={"project_id": project.id},
            values={"is_favorites": False},
        )


async def add_user_to_project(
    login: str,
    project_id: int,
    session: AsyncSession,
    user: UserInfo
):
    """
    Добавление пользователя в проект
    добавить можно только зарегестрированного пользователя (пока что)
    """
    # может ли текущий пользователь добавлять кого-то в проект
    check_root = await check_link_owner(project_id, user.id, session)
    # берем id пользователя, которого хотим добавить в проект
    user_id_query = await session.execute(
        select(UserInfo.id).
        where(UserInfo.login == login)
    )
    user_id = user_id_query.scalar_one_or_none()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="пользователь не найден")
    if check_root:
        try:
            await ProjectUserDAO.insert_data(
                session=session,
                data={
                    "user_id": user_id,
                    "project_id": project_id,
                }
            )
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="пользователь уже в проекте")
        

async def remove_user_from_project(
    user_id: int,
    project_id: int,
    user: UserInfo,    
    session: AsyncSession,
):
    """
    Удаление пользователя из проекта
    себя удалить нельзя
    """
    # сначала проверим, является ли пользователь админом, чтобы выполнять такие действия
    check_root = await check_link_owner(project_id, user.id, session)
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="неприемлемое действие")
    if check_root:
        # удаляем связку проект-пользователь
        await ProjectUserDAO.delete_data(
            session=session,
            filters={
                "project_id": project_id,
                "user_id": user_id,
            }
        )
        # проверим есть ли еще пользователи в проекте помимо админа
        exist_users_query = await session.execute(
            select(ProjectUser.user_id).
            where(ProjectUser.project_id == project_id).
            where(ProjectUser.user_id != user.id)
        )
        exist_users = exist_users_query.scalars().all()
        # если нет, то вешаем все задачи на админа (единственного пользователя)
        new_executor = None
        if not exist_users:
            new_executor = user.id
            
        await TaskDAO.update_data(
            session=session,
            filters={
                "executor_id": user_id,
                "project_id": project_id,
            },
            values={'executor_id': new_executor}
        )


async def project_user_list(project_id: int, user: UserInfo, session: AsyncSession):
    """
    Получить список пользователей в проекте
    """
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
    """
    Выдать/забрать админские права проекта
    """
    check_root = await check_link_owner(project_id, user.id, session)
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="неприемлемое действие")
    if check_root:
        await ProjectUserDAO.update_data(
            session=session,
            filters={
                "project_id": project_id,
                "user_id": user_id,
            },
            values={"is_owner": is_owner}
        )