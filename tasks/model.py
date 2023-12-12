from __future__ import annotations

from typing import List

from pydantic import BaseModel
from datetime import datetime


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
    project_id: int | None
    project_name: str = "Входящие"
    section_id: int | None = None
    section_name: str | None = None
    status: bool
    id: int
    name: str
    owner: str


class CreateTask(_Base):
    owner: str = None
    name: str
    description: str
    section_id: int | None = None
    project_id: int | None = None


class EditTask(_Base):
    id: int
    name: str = "New name"
    description: str = "New description"
    section_id: int | None = None
    project_id: int | None = None
    status: bool = True


class ErrorNotFound(_Base):
    message: str = "тут будет сообщение об ошибке"