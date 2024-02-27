from dao.base import BaseDAO
from database.schemas import User, UserInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


class UsersDAO(BaseDAO):
    schema = User
    info_chema = UserInfo

    @classmethod
    async def find_by_id(cls, session: AsyncSession, arg):
        query = select(cls.info_chema).filter_by(id=arg)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def check_user(cls, session: AsyncSession, arg):
        query = await session.execute(
            select(
                cls.schema.login,
                cls.schema.password,
                cls.info_chema.id,
            ).
            join(cls.info_chema).
            where(cls.schema.login == arg))
        result = query.one_or_none()
        return result
    
    @classmethod
    async def create_user(cls, session: AsyncSession, data):
        await session.execute(
            insert(cls.info_chema).
            values(**data)
        )
        await session.commit()