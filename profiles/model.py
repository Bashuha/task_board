from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class UserChangeFIO(_Base):
    first_name: str | None
    second_name: str | None


class UserChangeEmail(_Base):
    ...


class UserChangePass(_Base):
    ...