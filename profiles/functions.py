from database.schemas import Project, User, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func, or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
import profiles.model as profile_model
from fastapi import status, HTTPException
from datetime import datetime


async def delete_user_from_system(user: UserInfo, session: AsyncSession):
    """
    Удалить пользователя из системы
    - удалить все проекты, где он единственный пользователь
    - удалить его из всех остальных проектов (связь в project_user)
    """
    # сначала берем все проекты в которых мы есть
    project_ids_query = await session.execute(
        select(ProjectUser.project_id).
        where(ProjectUser.user_id == user.id)
    )
    project_ids = project_ids_query.scalars().all()
    # потом смотрим в каких проектах мы единственный юзер
    solo_project_query = await session.execute(
        select(
            func.IF(
                (func.count(ProjectUser.user_id) == 1),
                ProjectUser.project_id,
                None
            )
        ).
        where(ProjectUser.project_id.in_(project_ids)).
        group_by(ProjectUser.project_id)
    )
    solo_projects = set(solo_project_query.scalars().all())
    if None in solo_projects:
        solo_projects.remove(None)
    # удаляем эти проекты
    if solo_projects:
        await session.execute(
            delete(Project).
            where(Project.id.in_(solo_projects))
        )
        await session.commit()
    # удаляем пользователя
    await session.execute(
        delete(User).
        where(User.login == user.login)
    )
    await session.commit()


async def edit_profile(
    session: AsyncSession,
    profile_model: profile_model.EditProfile,
    user: UserInfo
):
    user_data = profile_model.model_dump(exclude_unset=True)
    if not user_data:
        return
    if new_login := user_data.get('email'):
        await session.execute(
            update(User).
            where(User.login == user.login).
            values(login=new_login)
        )
        await session.commit()
    else:
        await session.execute(
            update(UserInfo).
            where(UserInfo.id == user.id).
            values(user_data)
        )
        await session.commit()