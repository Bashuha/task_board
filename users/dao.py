from dao.base import BaseDAO
from database.schemas import User, UserInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


class UsersDAO(BaseDAO):
    schema = User

    @classmethod
    async def find_by_id(cls, session: AsyncSession, arg):
        query = select(cls.schema.id).filter_by(id=arg)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    
# class UserInfoDAO(BaseDAO):
#     schema = UserInfo

#     @classmethod
#     async def find_user_info(cls, session: AsyncSession, arg):
#         query = select(cls.schema.full_name).filter_by(login=arg)
#         result = await session.execute(query)
#         return result.scalar_one_or_none()