from pydantic import BaseModel


class _Base(BaseModel):

    class Config:
        from_attributes=True


class UserChangeFIO(_Base):
    first_name: str | None
    second_name: str | None


class UserChangeEmail(_Base):
    ...


class UserChangePass(_Base):
    ...