from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    schema = None

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **arg):
        query = select(cls.schema).filter_by(**arg)
        result = await session.execute(query)
        return result.one_or_none()
    
    @classmethod
    async def insert_data(cls, session: AsyncSession, **data):
        query = insert(cls.schema).values(**data)
        await session.execute(query)
        await session.commit()