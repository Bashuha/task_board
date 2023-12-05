from pydantic import BaseModel, EmailStr


class UserResgisetr(BaseModel):
    login: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    login: str
    password: str