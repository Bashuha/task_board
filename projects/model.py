from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class _Base(BaseModel):

    class Config:
        from_attributes=True


class SectionForDetails(_Base):
    value: int = Field(validation_alias='id')
    label: str = Field(validation_alias='name')
    order_number: int
    is_basic: bool


class TaskForDetails(_Base):
    id: int
    name: str
    description: str | None
    section_id: int | None
    status: bool
    comments_count: int
    order_number: int
    create_date: datetime


class ProjectDetails(_Base):
    id: int | None
    name: str
    is_favorites: bool
    sections: List[SectionForDetails]
    open_tasks: List[TaskForDetails]
    close_tasks: List[TaskForDetails]


class TodayTask(_Base):
    id: int
    name: str
    description: str
    status: bool
    project_id: int
    project_name: str
    section_id: int
    section_name: str
    comments_count: int


class TodayTaskList(_Base):
    task_list: List[TodayTask]


class SmallTask(_Base):
    id: int
    name: str
    description: str | None
    status: bool
    comments_count: int
    order_number: int
    create_date: datetime


class Section(_Base):
    value: int
    label: str
    order_number: int
    open_tasks: List[SmallTask]
    close_tasks: List[SmallTask]
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
    is_favorites: bool = False
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


