from sqlalchemy import select
from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import profiles.functions as profile_func
# from profiles.model import 
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