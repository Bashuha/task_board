from pydantic import BaseModel, HttpUrl, Field
from typing import List


class Task(BaseModel):
    id: int
    name: str = "Generic name"
    description: str | None = ""
    section_id: int | None = None
    project_id: int | None = None
    status: bool = True
    owner: str = "Ilusha"
    comments_count: int = 0


class Section(BaseModel):
    id: int
    name: str
    project_id: int = 0
    tasks: List[Task] = []


class Project(BaseModel):
    id: int
    name: str = "Nameless"
    is_favorites: bool = False
    is_archive: bool = False
    tasks: List[Task] = []
    sections: List[Section] = []


class ProjectForList(BaseModel):
    project_name: str
    is_favorites: bool
    is_archive: bool
    id: int
    task_count: int
    sections: List[Section]


class ProjectList(BaseModel):
    projects: List[ProjectForList]





class Comment(BaseModel):
    task_id: int
    id: int
    text: str

 