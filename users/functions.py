from . import model
from users.dao import UsersDAO
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, insert, join
from jose import jwt, JWTError
from database.config import JWT
from datetime import datetime, timedelta
from database.schemas import UserInfo, User
from fastapi import Request, Response, status, HTTPException, Depends


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def register_user(user_data: model.UserResgisetr, session: AsyncSession):
    existing_user = await UsersDAO.find_one_or_none(login=user_data.login, session=session)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="такой пользователь уже существует")
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.insert_data(login=user_data.login, password=hashed_password, session=session)
    await session.execute(insert(UserInfo).values(login=user_data.login, full_name=user_data.full_name))


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JWT.get("secret"), JWT.get('algoritm')
    )
    return encoded_jwt


async def login_user(response: Response, user_data: model.UserLogin, session: AsyncSession):
    user: User = await UsersDAO.find_one_or_none(login=user_data.login, session=session)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="введены неверные данные")
    access_token = create_token(
        {
            "sub": str(user.id)
        }
    )
    response.set_cookie("oil_token", access_token, httponly=True)
    return {"access_token": access_token}


def get_token(request: Request):
    token = request.cookies.get('task_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user(session: AsyncSession, token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, JWT.get("secret"), JWT.get('algoritm')
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неправильный токен")
    expire: str = payload.get("exp")
    if not expire or int(expire) < datetime.utcnow().timestamp():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='время сессии истекло, перезайдите')
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='ошибка токена')
    user = await UsersDAO.find_by_id(arg=int(user_id), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='такого пользователя не существует')
    return user