from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
import tags.model as tag_model
from fastapi import HTTPException, status
from database.schemas import Task, UserInfo, Tag, tag_task_link
from projects.functions import check_user_project


async def get_tag_list(
    session: AsyncSession,
    user: UserInfo,
    project_id: int,
):
    await check_user_project(project_id, user.id, session)

    tag_query = await session.execute(
        select(Tag).
        where(Tag.project_id == project_id)
    )
    tag_list = tag_query.scalars().all()
    tag_object = tag_model.TagList(tags=tag_list)
    return tag_object


async def create_tag(
    session: AsyncSession,
    tag_model: tag_model.CreateTag,
    user: UserInfo,
):
    await check_user_project(tag_model.project_id, user.id, session)

    tag_dict = tag_model.model_dump(exclude_unset=True)
    await session.execute(insert(Tag).values(**tag_dict))
    await session.commit()


async def edit_tag(
    session: AsyncSession,
    tag_model: tag_model.EditTag,
    user: UserInfo
):
    await check_user_project(tag_model.project_id, user.id, session)

    tag_dict = tag_model.model_dump(exclude={"id"}, exclude_unset=True)
    await session.execute(
        update(Tag).
        values(**tag_dict).
        where(Tag.id == tag_model.id, Tag.project_id == tag_model.project_id)
    )
    await session.commit()


async def delete_tag(
    session: AsyncSession,
    tag_model: tag_model.DeleteTag,
    user: UserInfo
):
    await check_user_project(tag_model.project_id, user.id, session)

    await session.execute(
        delete(Tag).
        where(
            Tag.id == tag_model.id,
            Tag.project_id == tag_model.project_id
        )
    )
    await session.commit()


async def add_tag_to_task(
    session: AsyncSession,
    tag_model: tag_model.ManageTag,
    user: UserInfo
):
    await check_user_project(tag_model.project_id, user.id, session)

    check_task_query = await session.execute(
        select(Task.id).
        where(
            Task.project_id == tag_model.project_id,
            Task.id == tag_model.task_id
        )
    )
    check_task = check_task_query.scalar_one_or_none()
    if not check_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='такой задачи в проекте нет')
    
    await session.execute(
        tag_task_link.insert().values(
            tag_id=tag_model.tag_id,
            task_id=tag_model.task_id
        )
    )
    await session.commit()


async def remove_tag_from_task(
    session: AsyncSession,
    tag_model: tag_model.ManageTag,
    user: UserInfo
):
    await check_user_project(tag_model.project_id, user.id, session)
    
    check_task_query = await session.execute(
        select(Task.id).
        where(Task.project_id == tag_model.project_id, Task.id == tag_model.task_id)
    )
    check_task = check_task_query.scalar_one_or_none()
    if not check_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='такой задачи в проекте нет')

    await session.execute(
        tag_task_link.delete().where(
            tag_task_link.c.tag_id == tag_model.tag_id,
            tag_task_link.c.task_id == tag_model.task_id
        )
    )
    await session.commit()