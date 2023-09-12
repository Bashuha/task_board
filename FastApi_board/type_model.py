from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class Project(BaseModel):
    id: int
    name: str = "Nameless"
    is_favorites: bool = False
    is_archive: bool = False


class Task(BaseModel):
    name: str
    description: str
    section_id: str | None = None
    project_id: str | None = None


class Section(BaseModel):
    name: str
    project_id: int
    id: int


class Comment(BaseModel):
    task_id: int
    id: int
    text: str

 