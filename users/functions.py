import users.model as user_model
from users.dao import UsersDAO
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from jose import jwt, JWTError
from database.schemas import UserInfo, Project
from database.config import JWT
from database.my_engine import get_db
from datetime import datetime, timedelta, timezone
from fastapi import Request, Response, status, HTTPException, Depends, WebSocket
from projects.model import CreateProject
from projects.functions import create_project


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    Проверка валидности пароля
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Хеширование пароля пользователя
    """
    return pwd_context.hash(password)


async def register_user(user_data: user_model.UserResgisetr, session: AsyncSession):
    """
    Создание пользователя в БД
    """
    existing_user = await UsersDAO.find_one_or_none(
        login=user_data.login, session=session
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="такой пользователь уже существует",
        )
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.insert_data(
        login=user_data.login, password=hashed_password, session=session
    )
    await UsersDAO.create_user(
        data=user_data.model_dump(exclude={"password"}), session=session
    )
    user_query = await session.execute(
        select(UserInfo).where(UserInfo.login == user_data.login)
    )
    user = user_query.scalar_one_or_none()
    project = CreateProject(name="Входящие")
    project_id = await create_project(project, user, session)
    await session.execute(
        update(Project).where(Project.id == project_id).values(is_incoming=True)
    )
    await session.commit()


def create_token(data: dict):
    """
    Генерация токена основываясь на данных пользователя
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT.get("secret"), JWT.get("alg"))
    return encoded_jwt


def update_token(user_id, login, response: Response):
    """
    Создание/обновление access и refresh токенов и запихивание их в куки
    """
    access_token = create_token(
        {
            "sub": user_id,
            "login": login,
            "type": "access"
        }
    )
    expire_access = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(
        minutes=10
    )
    response.set_cookie(
        "access_token", access_token, expires=expire_access, httponly=True
    )

    refresh_token = create_token(
        {
            "sub": user_id,
            "login": login,
            "type": "refresh"
        }
    )
    expire_refresh = datetime.now(timezone(timedelta(hours=3)).utc) + timedelta(days=30)
    response.set_cookie(
        "refresh_token", refresh_token, expires=expire_refresh, httponly=True
    )

    return access_token


async def login_user(
    response: Response, user_data: user_model.UserLogin, session: AsyncSession
):
    """
    Аутентификация пользователя в системе
    """    
    user = await UsersDAO.check_user(arg=user_data.login, session=session)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="введены неверные данные"
        )
    user_info = await UsersDAO.find_by_id(session=session, arg=user.id)
    update_token(user_id=str(user.id), login=user.login, response=response)

    return user_model.UserInfo.model_validate(user_info)


def get_token(request: Request, response: Response):
    """
    Проверка наличия токенов и обновление access токена при наличии refresh
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not access_token and refresh_token:
        try:
            payload = jwt.decode(refresh_token, JWT.get("secret"), JWT.get("algoritm"))
        except JWTError as e:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}"
        )
        access_token = update_token(
            user_id=payload.get("sub"),
            login=payload.get("login"),
            response=response
        )

    return access_token


async def get_current_user(
    token: str = Depends(get_token)
):
    """
    Проверка пользователя (залогинен или нет)
    """
    try:
        payload = jwt.decode(token, JWT.get("secret"), JWT.get("algoritm"))
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}"
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="не тот токен"
        )
    user = user_model.GetUser(id=payload.get("sub"), login=payload.get("login"))
    return user


def get_socket_token(request: WebSocket, response: Response):
    """
    Проверка наличия токенов и обновление access токена при наличии refresh
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not access_token and refresh_token:
        try:
            payload = jwt.decode(refresh_token, JWT.get("secret"), JWT.get("algoritm"))
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}"
            )
        access_token = update_token(
            user_id=payload.get("sub"),
            login=payload.get("login"),
            response=response
        )

    return access_token


async def websocket_user(
    token: str = Depends(get_socket_token)
):
    """
    Проверка пользователя (залогинен или нет)
    """
    try:
        payload = jwt.decode(token, JWT.get("secret"), JWT.get("algoritm"))
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}"
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="не тот токен"
        )
    user = user_model.GetUser(id=payload.get("sub"), login=payload.get("login"))
    return user


async def check_user():
    """
    Функция проверки пользователя для роута
    """
    return