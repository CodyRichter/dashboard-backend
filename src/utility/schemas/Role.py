from typing import List

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


from src.utility.schemas.User import User

Role.update_forward_refs()
