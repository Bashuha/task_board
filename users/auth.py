from database.my_engine import get_db
from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import model
import users.functions as auth_func
from users.functions import get_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: model.UserResgisetr,
    session: AsyncSession = Depends(get_db)
):
    await auth_func.register_user(user_data, session)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login_user(
    response: Response,
    user_data: model.UserLogin,
    session: AsyncSession = Depends(get_db)
):
    return await auth_func.login_user(response, user_data, session)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout_user(
    response: Response
):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


@router.get(
    "/check_user",
    status_code=status.HTTP_200_OK
)
async def check_user(request: Request, session: AsyncSession = Depends(get_db)):
    return await auth_func.check_user(request, session)