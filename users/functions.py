from . import model
from users.dao import UsersDAO
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from database.config import JWT
from database.my_engine import get_db
from datetime import datetime, timedelta, timezone
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
    await UsersDAO.create_user(
        data=user_data.model_dump(exclude={'password'}),
        session=session                                            
    )


def create_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(
        to_encode, JWT.get("secret"), JWT.get('alg')
    )
    return encoded_jwt


async def login_user(response: Response, user_data: model.UserLogin, session: AsyncSession):
    user = await UsersDAO.check_user(arg=user_data.login, session=session)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="введены неверные данные")
    user_info = await UsersDAO.find_by_id(session=session, arg=user.id)
    access_token = create_token(
        {
            "sub": str(user.id)
        }
    )
    expire_key = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(hours=12)
    response.set_cookie("access_token", access_token, expires=expire_key, httponly=True)
    return model.UserResgisetr.model_validate(user_info)


def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user(session: AsyncSession = Depends(get_db), token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, JWT.get("secret"), JWT.get('algoritm')
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неправильный токен")
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='ошибка токена')
    user = await UsersDAO.find_by_id(arg=int(user_id), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='такого пользователя не существует')
    return user