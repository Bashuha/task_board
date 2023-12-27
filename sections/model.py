from pydantic import BaseModel
from typing import List


class CreateSection(BaseModel):
    project_id: int
    name: str


class EditSection(BaseModel):
    id: int
    name: str
    project_id: int


class DeleteSection(BaseModel):
    id: int
    project_id: int


class Section(BaseModel):
    id: int


class SectionOrder(BaseModel):
    sections: List[Section]
    project_id: int


class NotFoundError(BaseModel):
    message: str = "тут будет сообщение об ошибке"


class BadRequestError(BaseModel):
    message: str = "Неверный формат данных"