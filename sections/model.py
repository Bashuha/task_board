from pydantic import BaseModel
from typing import List


class CreateSection(BaseModel):
    project_id: int
    name: str


class EditSection(BaseModel):
    id: int
    name: str


class Section(BaseModel):
    id: int


class SectionOrder(BaseModel):
    sections: List[Section]
    project_id: int