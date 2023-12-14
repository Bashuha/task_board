from pydantic import BaseModel, Field
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
    order_number: int


class Section(_Base):
    value: int
    label: str
    order_number: int
    tasks: List[SmallTask]
    is_basic: bool


class Project(_Base):
    id: int | None
    name: str
    is_favorites: bool
    sections: List[Section]


class IncomingTasks(_Base):
    name: str = "Входящие"
    tasks: List[SmallTask]


class CreateProject(_Base):
    name: str
    is_favorites: bool = False


class SectionForCreate(_Base):
    name: str = "Основной"
    project_id: int
    is_basic: bool = True
    order_number: int = 1


class EditProject(_Base):
    id: int
    name: str = "New name"
    is_favorites: bool = False


class ChangeArchiveStatus(_Base):
    id: int
    is_archive: bool


class SmallSection(_Base):
    value: int = Field(validation_alias='id')
    label: str = Field(validation_alias='name')
    project_id: int


class ProjectForList(_Base):
    label: str = Field(validation_alias='name')
    is_favorites: bool
    is_archive: bool
    value: int = Field(validation_alias='id')
    task_count: int = 0
    sections: List[SmallSection] = Field(validation_alias='sections')


class ProjectList(_Base):
    projects: List[ProjectForList]


class NotFoundError(_Base):
    message: str = "Проект не найден"


class BadRequestError(_Base):
    message: str = "Проект не в архиве"


