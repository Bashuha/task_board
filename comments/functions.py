from sqlalchemy import insert, update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from comments.model import CreateComment, EditComment
from fastapi import HTTPException, status
from database.schemas import Comments, Task, UserInfo


async def check_user(comment_id: int, session: AsyncSession, user: UserInfo):
    check_user_query = await session.execute(
        select(Comments.id).
        where(Comments.id == comment_id).
        where(Comments.login == user.login)
    )
    check_user = check_user_query.one_or_none()
    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='вы не можете взаимодействовать с этим комментарием')
    

async def create_comment(comment: CreateComment, session: AsyncSession, user: UserInfo):
    # доработать чтобы оставлять коменты только в проектах где ты есть
    task_qr = session.get(Task, comment.task_id)
    task: Task = await task_qr
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    
    comment_data = comment.model_dump()
    comment_data['login'] = user.login
    stmt = insert(Comments).values(comment_data)
    await session.execute(stmt)
    await session.commit()


async def edit_comment(comment: EditComment, session: AsyncSession, user: UserInfo):
    await check_user(comment.id, session, user)
    comment_data = comment.model_dump(exclude={'id'})
    update_query = update(Comments).where(Comments.id==comment.id).values(comment_data)
    await session.execute(update_query)
    await session.commit()


async def delete_comment(comment_id: int, session: AsyncSession, user: UserInfo):
    await check_user(comment_id, session, user)
    delete_query = delete(Comments).where(Comments.id==comment_id)
    await session.execute(delete_query)
    await session.commit()