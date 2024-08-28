from dao.base import BaseDAO
from database.schemas import Comments


class CommentDAO(BaseDAO):
    schema = Comments