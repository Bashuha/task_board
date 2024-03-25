from __future__ import annotations

from typing import List, Any

from pydantic import BaseModel, model_validator, Field
from datetime import datetime, date



class _Base(BaseModel):

    class Config:
        from_attributes=True


class CreateTag(_Base):
    name: str
    project_id: int
    color_id: int


class TagColor(_Base):
    id: int
    name: str
    color: str


class TagColors(_Base):
    colors: List[TagColor]


class TagInfo(_Base):
    id: int
    name: str
    project_id: int
    color_id: int


class TagList(_Base):
    tags: List[TagInfo]


class EditTag(_Base):
    id: int
    project_id: int
    name: str = None
    color_id: int = None


class DeleteTag(_Base):
    id: int
    project_id: int


class TagIds(_Base):
    id: int


class ManageTag(_Base):
    tag_ids: List[TagIds]
    task_id: int
    project_id: int

    def sort_ids(self):
        sorted_ids = sorted(self.tag_ids, key=lambda tag: tag.id)
        return sorted_ids



class TagIDList(_Base):
    ids: List[int]

    @model_validator(mode="after")
    def sort_ids(self):
        self.ids = sorted(self.ids)
        return self