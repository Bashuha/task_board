from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from comments.model import CreateComment, EditComment
from fastapi import HTTPException
from database.schemas import Comments, Task


async def create_comment(comment: CreateComment, session: AsyncSession):
    task_qr = session.get(Task, comment.task_id)
    task: Task = await task_qr
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    
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
    comment_qr = session.get(Comments, comment_id)
    comment: Comments = await comment_qr
    if not comment:
        raise HTTPException(detail='Раздел не найдена', status_code=404)
    
    delete_query = delete(Comments).where(Comments.id==comment_id)
    await session.execute(delete_query)
    await session.commit()