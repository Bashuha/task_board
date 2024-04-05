from sqlalchemy import insert, tuple_, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
import tags.model as tag_models
from fastapi import HTTPException, status
from database.schemas import Task, UserInfo, Tag, tag_task_link, TagColor
from projects.functions import check_user_project


async def get_tag_list(
    session: AsyncSession,
    user: UserInfo,
    project_id: int,
):
    """
    Получаем список всех тегов проекта
    """
    await check_user_project(project_id, user.id, session)

    tag_query = await session.execute(
        select(Tag).
        where(Tag.project_id == project_id)
    )
    tag_list = tag_query.scalars().all()
    tag_object = tag_models.TagList(tags=tag_list)
    return tag_object


async def create_tag(
    session: AsyncSession,
    tag_model: tag_models.CreateTag,
    user: UserInfo,
):
    """
    Создаем тег внутри конкретного проекта
    """
    await check_user_project(tag_model.project_id, user.id, session)

    tag_dict = tag_model.model_dump(exclude_unset=True)
    tag_query = await session.execute(
        insert(Tag).
        values(tag_dict)
    )
    tag_id = tag_query.lastrowid
    await session.commit()
    return tag_id


async def edit_tag(
    session: AsyncSession,
    tag_model: tag_models.EditTag,
    user: UserInfo
):
    """
    Редактировать тег конкретного проекта
    """
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
    tag_model: tag_models.DeleteTag,
    user: UserInfo
):
    """
    Удалить тег внутри конкретного проекта
    """
    await check_user_project(tag_model.project_id, user.id, session)

    await session.execute(
        delete(Tag).
        where(
            Tag.id == tag_model.id,
            Tag.project_id == tag_model.project_id
        )
    )
    await session.commit()


async def remove_tag_from_task(
    session: AsyncSession,
    task_id: int,
):
    """
    Открепить теги от задачи
    """
    # value_list = list()
    # for tag_id in tag_ids:
    #     tag_values = (tag_id, task_id)
    #     value_list.append(tag_values)

    await session.execute(
        tag_task_link.delete().
        where(tag_task_link.c.task_id == task_id)
    )

    # await session.execute(
    #     tag_task_link.delete().
    #     where(tuple_(tag_task_link.c.tag_id, tag_task_link.c.task_id).in_(value_list))
    # )

    await session.commit()


async def change_task_tags(
    session: AsyncSession,
    incoming_ids: list[int],
    project_id: int,
    task_id: int,
):
    """
    Прикрепить тег к задаче
    """
    exist_tag_query = await session.execute(
        select(Tag.id).
        where(Tag.project_id == project_id).
        order_by(Tag.id)
    )
    exist_tag_ids = exist_tag_query.scalars().all()
    tag_project_check = set(incoming_ids).issubset(exist_tag_ids)
    if tag_project_check:
        await remove_tag_from_task(session, task_id)

        value_list = list()
        if incoming_ids:
            for tag_id in incoming_ids:
                tag_dict = {
                    "tag_id": tag_id,
                    "task_id": task_id
                }
                value_list.append(tag_dict)

            await session.execute(
                tag_task_link.insert().values(
                    value_list
                )
            )
            await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="переданы несуществующие теги")


async def get_tag_colors(
    session: AsyncSession,
):
    color_query = await session.execute(
        select(TagColor)
    )
    color_list: list[TagColor] = color_query.scalars().all()
    colors = tag_models.TagColors(colors=color_list)
    return colors