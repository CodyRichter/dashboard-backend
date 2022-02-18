from typing import Optional, List

from pydantic import BaseModel


class PrizeBase(BaseModel):
    title: str
    description: Optional[str]
    reward: str
    sponsor: Optional[str]
    priority: int
    selectable: bool


class PrizeCreate(PrizeBase):
    pass


class Prize(PrizeBase):
    id: int
    # winning_projects: "List[Project]"

    class Config:
        orm_mode = True


from src.utility.schemas.Project import Project  # noqa
Prize.update_forward_refs()
