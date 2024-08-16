from pydantic import BaseModel


class CreateComment(BaseModel):
    project_id : int
    task_id: int
    text: str


class EditComment(BaseModel):
    id: int
    text: str


class DeleteComment(BaseModel):
    id: int
    project_id: int
    task_id: int


class NotFoundError(BaseModel):
    message: str = "тут будет сообщение об ошибке"