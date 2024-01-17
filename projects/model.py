from pydantic import BaseModel, Field, model_validator
from typing import List, Any
from datetime import date, datetime


class _Base(BaseModel):

    class Config:
        from_attributes=True


class UserInfo(_Base):
    id: int
    login: str
    first_name: str
    second_name: str


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
    comments_count: Any = Field(validation_alias="comments")
    order_number: int
    create_date: datetime
    to_do_date: date | None
    owner_info: UserInfo | None
    executor_info: UserInfo | None
    task_giver_info: UserInfo | None

    @model_validator(mode='after')
    def change_field(self):
        self.comments_count: int = len(self.comments_count)
        return self


class ProjectDetails(_Base):
    id: int | None
    name: str
    is_favorites: bool
    me_admin: bool
    users_count: int
    sections: List[SectionForDetails]
    open_tasks: List[TaskForDetails]
    close_tasks: List[TaskForDetails]


class TodayTask(_Base):
    id: int
    name: str
    description: str
    status: bool
    project_id: int
    section_id: int
    project_name: Any = Field(validation_alias='project')
    section_name: Any = Field(validation_alias='sections')
    comments_count: Any = Field(validation_alias="comments")

    @model_validator(mode='after')
    def change_field(self):
        self.project_name: str = self.project_name.name
        self.section_name: str = self.section_name.name
        self.comments_count: int = len(self.comments_count)
        return self


class TodayTaskList(_Base):
    today_tasks: List[TodayTask]
    outstanding_tasks: List[TodayTask]


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
    is_incoming: bool
    value: int = Field(validation_alias='id')
    users_count: Any = Field(validation_alias='user_link')
    task_count: int = 0
    sections: List[SmallSection] = Field(validation_alias='sections')

    @model_validator(mode='after')
    def change_field(self):
        self.users_count: int = len(self.users_count)
        return self


class ProjectList(_Base):
    projects: List[ProjectForList]


class ProjectUserInfo(_Base):
    value: int = Field(validation_alias="user_id")
    is_owner: bool
    label: Any = None
    first_name: str
    second_name: str
    login: str

    @model_validator(mode='after')
    def change_field(self):
        self.label: str = f"{self.first_name} {self.second_name} ({self.login})"
        return self


class ProjectUserList(_Base):
    users_list: List[ProjectUserInfo]


class NotFoundError(_Base):
    message: str = "Проект не найден"


class BadRequestError(_Base):
    message: str = "Проект не в архиве"


