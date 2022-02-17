from typing import Optional, List

from pydantic import BaseModel


class UserBaseModel(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserCreate(UserBaseModel):
    password: str


class User(UserBaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    disabled: bool = False

    roles: list[str] = []

    class Config:
        orm_mode = True