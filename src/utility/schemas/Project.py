from typing import List

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str
    image_url: str
    github_link: str
    video_link: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    prizes_won: "List[Prize]"


from src.utility.schemas.Prize import Prize  # noqa
Project.update_forward_refs()
