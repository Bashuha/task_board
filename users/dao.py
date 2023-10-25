from dao.base import BaseDAO
from database.schemas import Users


class UsersDAO(BaseDAO):
    schema = Users