from dao.base import BaseDAO
from database.schemas import Project, ProjectUser


class ProjectDAO(BaseDAO):
    schema = Project


class ProjectUserDAO(BaseDAO):
    schema = ProjectUser


