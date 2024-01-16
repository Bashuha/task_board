from pydantic import BaseModel


class CreateComment(BaseModel):
    task_id: int
    text: str


class EditComment(BaseModel):
    id: int
    text: str


class NotFoundError(BaseModel):
    message: str = "тут будет сообщение об ошибке"