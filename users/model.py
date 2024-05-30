from pydantic import BaseModel, EmailStr


class _Base(BaseModel):

    class Config:
        from_attributes=True


class UserResgisetr(_Base):
    login: str
    password: str
    first_name: str
    second_name: str


class UserLogin(_Base):
    login: str
    password: str


class UserInfo(_Base):
    id: int
    login: str
    first_name: str
    second_name: str


class GetUser(_Base):
    id: int
    login: str