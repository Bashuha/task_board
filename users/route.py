from fastapi import APIRouter
from . import model
import users.functions as user_func
from fastapi import Depends
from database.my_engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
async def register_user(user_data: model.UserResgisetr, session: AsyncSession = Depends(get_db)):
    return await user_func.register_user(user_data, session)