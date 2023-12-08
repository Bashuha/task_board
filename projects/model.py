from pydantic import BaseModel
from typing import List


class _Base(BaseModel):

    class Config:
        from_attributes=True


class SmallTask(_Base):
    id: int
    name: str
    description: str | None
    status: bool
    comments_count: int


class Section(_Base):
    value: int
    label: str
    order_number: int
    tasks: List[SmallTask]


class Project(_Base):
    id: int | None
    name: str
    is_favorites: bool
    tasks: List[SmallTask]
    sections: List[Section]


class IncomingTasks(_Base):
    name: str = "Входящие"
    tasks: List[SmallTask]


class CreateProject(_Base):
    name: str
    is_favorites: bool = False


class EditProject(_Base):
    id: int
    name: str = "New name"
    is_favorites: bool = False


class ChangeArchiveStatus(_Base):
    id: int
    is_archive: bool


class SmallSection(_Base):
    value: int
    label: str
    project_id: int


class ProjectForList(_Base):
    label: str
    is_favorites: bool
    is_archive: bool
    value: int
    task_count: int
    sections: List[SmallSection]


class ProjectList(_Base):
    projects: List[ProjectForList]


class NotFoundError(_Base):
    message: str = "Проект не найден"


class BadRequestError(_Base):
    message: str = "Проект не в архиве"


