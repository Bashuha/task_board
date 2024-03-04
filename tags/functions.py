from sqlalchemy import insert, update, delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
import tags.model as tag_model
from fastapi import HTTPException, status
from database.schemas import ProjectTag, UserInfo, Tag
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
    tag_data = Tag(**tag_dict)
    session.add(tag_data)
    await session.commit()
    await session.flush()
    await session.refresh(tag_data)
    session.add(ProjectTag(tag_id=tag_data.id, project_id=tag_model.project_id))
    # await session.execute(insert(ProjectTag).values(tag_id=tag_data.id, project_id=tag_model.project_id))
    await session.commit()
