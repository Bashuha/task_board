from pydantic import BaseModel
from typing import List


class SmallTask(BaseModel):
    id: int
    name: str
    description: str | None
    status: bool
    comments_count: int


class Section(BaseModel):
    id: int
    name: str
    tasks: List[SmallTask]


class Project(BaseModel):
    id: int
    name: str
    is_favorites: bool
    tasks: List[SmallTask]
    sections: List[Section]


class CreateProject(BaseModel):
    name: str
    is_favorites: bool


class EditProject(BaseModel):
    id: int
    name: str = "New name"
    is_favorites: bool = False


class ChangeArchiveStatus(BaseModel):
    id: int
    is_archive: bool


class SmallSection(BaseModel):
    id: int
    name: str
    project_id: int


class ProjectForList(BaseModel):
    project_name: str
    is_favorites: bool
    is_archive: bool
    id: int
    task_count: int
    sections: List[SmallSection]


class ProjectList(BaseModel):
    projects: List[ProjectForList]