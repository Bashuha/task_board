from pydantic import BaseModel, EmailStr


class UserResgisetr(BaseModel):
    login: EmailStr
    password: str