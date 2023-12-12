from pydantic import BaseModel, EmailStr


class UserResgisetr(BaseModel):
    login: str
    password: str
    first_name: str
    second_name: str
    last_name: str


class UserLogin(BaseModel):
    login: str
    password: str