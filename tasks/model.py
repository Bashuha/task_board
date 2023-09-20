from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Comment(BaseModel):
    create_at: str
    id: int
    login: str
    text: str


class Task(BaseModel):
    comments: List[Comment]
    create_date: str
    description: str | None
    project_id: int
    project_name: str
    section_id: int | None
    section_name: str | None
    status: bool
    id: int
    task_name: str
    task_owner: str


class CreateTask(BaseModel):
    owner: str = None
    name: str
    description: str
    section_id: int | None = None
    project_id: int | None = None


class EditTask(BaseModel):
    id: int
    name: str = "New name"
    description: str = "New description"
    section_id: int | None = None
    project_id: int | None = None
    status: bool = True


class ErrorNotFound(BaseModel):
    message: str = "тут будет сообщение об ошибке"