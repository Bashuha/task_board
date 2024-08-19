from database.schemas import Project, Task, Comments, UserInfo, ProjectUser
from sqlalchemy import insert, update, select, delete, func, or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
# import profile.model as profile_model
from fastapi import status, HTTPException
import projects.model as my_model
from datetime import datetime


async def delete_user(user: UserInfo, session: AsyncSession):
    """
    Удалить пользователя из системы
    - удалить все проекты, где он единственный пользователь
    - удалить его из всех остальных проектов (связь в project_user)
    - заменить его id в задачах на NULL
    - удалить все его комментарии
    """
    project_ids_query = await session.execute(
        select(ProjectUser.project_id)
    )
    project_ids = project_ids_query.scalars().all()
    ...