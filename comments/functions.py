from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import CompileError
from comments.model import CreateComment, DeleteComment, EditComment
from fastapi import HTTPException, status
from database.schemas import Comments, UserInfo
from projects.functions import check_user_project, check_link_owner
from comments.dao import CommentDAO
    

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
    comment_data['user_id'] = user.id
    try:
        await CommentDAO.insert_data(
            session=session,
            data=comment_data,
        )
    except CompileError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{e}')


async def edit_comment(
    comment: EditComment,
    session: AsyncSession,
    user: UserInfo
):
    """
    Редактирование своего комента
    """
    try:
        await CommentDAO.update_data(
            session=session,
            filters={
                "id": comment.id,
                "user_id": user.id,
            },
            values={'text': comment.text}
        )
    except CompileError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{e}')
    

async def delete_comment(
    comment_model: DeleteComment,
    session: AsyncSession,
    user: UserInfo
):
    """
    Удаление комментария
    Удалять коменты может либо автор комментария либо админ проекта
    """
    # если пользователь админ то комент можно удалить
    check_root = await check_link_owner(comment_model.project_id, user.id, session)
    if check_root:
        await CommentDAO.delete_data(
            session=session,
            filters={'id': comment_model.id}
        )
    # если пользователь не админ, но автор, то комент удалится
    else:
        await CommentDAO.delete_data(
            session=session,
            filters={
                "id": comment_model.id,
                "user_id": user.id,
            }
        )