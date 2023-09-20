from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from comments.model import CreateComment, EditComment
from fastapi import HTTPException, status
from database.schemas import Comments, Task


async def create_comment(comment: CreateComment, session: AsyncSession):
    task_qr = session.get(Task, comment.task_id)
    task: Task = await task_qr
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
    
    comment_data = comment.model_dump()
    comment_data['login'] = "Ilusha Developer"
    stmt = insert(Comments).values(comment_data)
    await session.execute(stmt)
    await session.commit()


async def edit_comment(comment: EditComment, session: AsyncSession):
    comment_data = comment.model_dump(exclude={'id'})
    update_query = update(Comments).where(Comments.id==comment.id).values(comment_data)
    await session.execute(update_query)
    await session.commit()


async def delete_comment(comment_id: int, session: AsyncSession):
    delete_query = delete(Comments).where(Comments.id==comment_id)
    await session.execute(delete_query)
    await session.commit()