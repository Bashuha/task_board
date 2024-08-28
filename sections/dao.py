from dao.base import BaseDAO
from database.schemas import Sections


class SectionDAO(BaseDAO):
    schema = Sections