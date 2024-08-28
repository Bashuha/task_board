from database.schemas import Project, User, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import profiles.model as profile_model
from users.dao import UsersDAO, UsersDAOInfo
from projects.dao import ProjectDAO
from users.functions import verify_password, get_password_hash
from fastapi import status, HTTPException


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
    await UsersDAO.delete_data(
        session=session,
        filters={"login": user.login}
    )


async def edit_profile(
    session: AsyncSession,
    profile_model: profile_model.EditProfile,
    user: UserInfo
):
    """
    Изменяет Фамилию Имя пользователя
    Изменяет почту пользователя (изменить, когда сделаем верификацию)
    """
    user_data = profile_model.model_dump(exclude_unset=True)
    if user_data.get('email'):
        await UsersDAO.update_data(
            session=session,
            filters={"login": user.login},
            values={"login": user_data.pop('email')}
        )

    if not user_data:
        return
    else:
        await UsersDAOInfo.update_data(
            session=session,
            filters={"id": user.id},
            values=user_data
        )


async def change_password(
    session: AsyncSession,
    pass_model: profile_model.UserChangePass,
    user: UserInfo,
):
    """
    Меняет пароль пользователю
    """
    user_data: User = await UsersDAO.find_one_or_none(
        session=session,
        filters={"login": user.login},
    )
    check_old_pass = verify_password(pass_model.old_pass, user_data.password)
    if not check_old_pass:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="неправильный пароль")
    hashed_password = get_password_hash(pass_model.new_pass)
    await UsersDAO.update_data(
        session=session,
        filters={"login": user.login},
        values={"password": hashed_password}
    )