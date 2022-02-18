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
    
    role: Optional["Role"] = None
    project: Optional["Project"] = None

    class Config:
        orm_mode = True


from src.utility.schemas.Role import Role  # noqa
from src.utility.schemas.Project import Project  # noqa

User.update_forward_refs()
