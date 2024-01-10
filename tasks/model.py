from __future__ import annotations

from typing import List

from pydantic import BaseModel
from datetime import datetime, date


class _Base(BaseModel):

    class Config:
        from_attributes=True


class Comment(_Base):
    create_at: datetime
    id: int
    login: str
    text: str


class Task(_Base):
    comments: List[Comment]
    create_date: datetime
    description: str | None
    project_id: int
    project_name: str
    section_id: int
    section_name: str
    to_do_date: date | None
    status: bool
    id: int
    name: str
    owner: str


class TaskForList(_Base):
    id: int
    project_id: int
    section_id: int
    comments_count:int
    name: str
    project_name: str
    section_name: str
    to_do_date: date


class TaskList(_Base):
    task_list: List[TaskForList]


class CreateTask(_Base):
    name: str
    description: str | None = None
    to_do_date: date | None = None
    section_id: int
    project_id: int


class EditTask(_Base):
    id: int
    name: str = "New name"
    description: str = "New description"
    section_id: int | None = None
    project_id: int | None = None
    status: bool = True
    order_number: int | None = None
    to_do_date: date | None = None


class ErrorNotFound(_Base):
    message: str = "тут будет сообщение об ошибке"


class TaskForOrder(_Base):
    id: int


class TaskOrder(_Base):
    tasks: List[TaskForOrder]
    section_id: int
    task_id: int