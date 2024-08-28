from sqlalchemy import select
from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import profiles.functions as profile_func
import profiles.model as profile_model
from users.functions import get_current_user, websocket_user, get_socket_token
from database.schemas import ProjectUser, UserInfo


router = APIRouter(
    tags=['User Profile']
)


@router.delete(
    '/delete_user',
    status_code=status.HTTP_200_OK,
    summary="Удаление пользователя из системы"
)
async def delete_user_from_system(
    # model_name: model_name.model_name,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await profile_func.delete_user_from_system(user, session)


@router.patch(
    '/edit_profile',
    status_code=status.HTTP_200_OK,
    summary="изменить данные в профиле"
)
async def edit_profile(
    profile_model: profile_model.EditProfile,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await profile_func.edit_profile(session, profile_model, user)


@router.put(
    '/change_pass',
    status_code=status.HTTP_200_OK,
    summary="смена пароля пользователя"
)
async def change_password(
    pass_model: profile_model.UserChangePass,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await profile_func.change_password(session, pass_model, user)