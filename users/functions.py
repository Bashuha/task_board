from . import model
from users.dao import UsersDAO
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def ligin_user(user_data: model.UserResgisetr):
    pass


async def register_user(user_data: model.UserResgisetr, session: AsyncSession):
    existing_user = await UsersDAO.find_one_or_none(login=user_data.login, session=session)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже сущетсвует")
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.insert_data(login=user_data.login, password=hashed_password, session=session)