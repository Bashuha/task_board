from __future__ import annotations

from typing import List, Any

from pydantic import BaseModel, model_validator, Field
from datetime import datetime, date


class _Base(BaseModel):

    class Config:
        from_attributes=True


class UserInfo(_Base):
    id: int
    login: str
    first_name: str
    second_name: str


class Comment(_Base):
    create_at: datetime
    id: int
    login: str
    text: str


class TagInfo(_Base):
    id: int
    name: str
    color_id: int


class Task(_Base):
    comments: List[Comment]
    create_date: datetime
    description: str | None
    project_id: int
    section_id: int 
    project_name: Any = Field(validation_alias='project')
    section_name: Any = Field(validation_alias='sections')
    to_do_date: date | None
    status: bool
    id: int
    name: str
    owner_info: UserInfo | None
    executor_info: UserInfo | None
    task_giver_info: UserInfo | None
    tags: List[TagInfo] = Field(validation_alias='tag_info')

    @model_validator(mode='after')
    def change_field(self):
        self.project_name = self.project_name.name
        self.section_name = self.section_name.name
        return self


class TaskForList(_Base):
    id: int
    project_id: int
    section_id: int
    description: str
    comments_count: Any = Field(validation_alias='comments')
    name: str
    project_name: Any = Field(validation_alias='project')
    section_name: Any = Field(validation_alias='sections')
    to_do_date: date | None
    tags: List[TagInfo] = Field(validation_alias='tag_info')

    @model_validator(mode='after')
    def change_field(self):
        self.project_name: str = self.project_name.name
        self.section_name: str = self.section_name.name
        self.comments_count: int = len(self.comments_count)
        return self


class TaskList(_Base):
    task_list: List[TaskForList]


class CreateTask(_Base):
    name: str
    description: str | None = None
    to_do_date: date | None = None
    executor_id: int | None = None
    section_id: int


class EditTask(_Base):
    id: int
    name: str = "New name"
    executor_id: int | None = None
    description: str = "New description"
    section_id: int | None = None
    to_do_date: date | None = None
    tag_ids: List[int] | None = None

    @model_validator(mode="after")
    def sort_ids(self):
        self.tag_ids = sorted(self.tag_ids)
        return self


class ChangeTaskStatus(_Base):
    id: int
    project_id: int
    section_id: int
    status: bool


class DeleteTask(_Base):
    task_id: int
    project_id: int


class ErrorNotFound(_Base):
    message: str = "тут будет сообщение об ошибке"


class TaskForOrder(_Base):
    id: int


class TaskOrder(_Base):
    tasks: List[TaskForOrder]
    section_id: int
    task_id: int
    project_id: int


# class TaskOrder(_Base):
#     # tasks: List[TaskForOrder]
#     project_id: int
#     task_start: int
#     task_end: int
#     section_start: int
#     section_end: int