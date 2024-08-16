from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import CompileError
from comments.model import CreateComment, DeleteComment, EditComment
from fastapi import HTTPException, status
from database.schemas import Comments, Task, UserInfo
from projects.functions import check_user_project, check_link_owner
    

async def create_comment(
    comment: CreateComment,
    session: AsyncSession,
    user: UserInfo
):
    """
    Создание комента у задачи
    """
    comment_data = comment.model_dump()
    await check_user_project(comment_data.pop('project_id'), user.id, session)
    comment_data['login'] = user.login
    try:
        await session.execute(
            insert(Comments).
            values(comment_data)
        )
        await session.commit()
    except CompileError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='ошибка создания комментария')


async def edit_comment(
    comment: EditComment,
    session: AsyncSession,
    user: UserInfo
):
    """
    Редактирование своего комента
    """
    try:
        await session.execute(
            update(Comments).
            where(
                Comments.id == comment.id,
                Comments.login == user.login
            ).
            values(text=comment.text)
        )
        await session.commit()
    except CompileError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='ошибка редактирования комментария')
    

async def delete_comment(
    comment_model: DeleteComment,
    session: AsyncSession,
    user: UserInfo
):
    """
    Удаление комментария
    Удалять коменты может либо автор комментария либо админ проекта
    """
    # если пользователь админ и такая задача существует, то комент можно удалить
    check_root = await check_link_owner(comment_model.project_id, user.id, session)
    check_task_query = await session.execute(
        select(Task.id).
        where(
            Task.id == comment_model.task_id,
            Task.project_id == comment_model.project_id
        )
    )
    task_id = check_task_query.scalar_one_or_none()
    if not task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='задача не найдена')
    if check_root and task_id:
        await session.execute(
            delete(Comments).
            where(
                Comments.id == comment_model.id,
                Comments.task_id == task_id,
            )
        )
    # если пользователь не админ, но автор и задача существует, то комент удалится
    elif task_id:
        await session.execute(
            delete(Comments).
            where(
                Comments.id == comment_model.id,
                Comments.login == user.login
            )
        )
    await session.commit()