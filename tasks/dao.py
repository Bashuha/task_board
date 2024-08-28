from dao.base import BaseDAO
from database.schemas import Task


class TaskDAO(BaseDAO):
    schema = Task