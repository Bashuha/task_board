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
    color: str | None = None


class TagInfo(_Base):
    id: int
    name: str
    project_id: int
    color: str | None = None


class TagList(_Base):
    tags: List[TagInfo]


class EditTag(_Base):
    id: int
    project_id: int
    name: str = None
    color: str | None = None


class DeleteTag(_Base):
    id: int
    project_id: int


class ManageTag(_Base):
    tag_id: int
    task_id: int
    project_id: int