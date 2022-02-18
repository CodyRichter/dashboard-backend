from typing import List, Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    image_url: str
    github_link: str
    video_link: str
    description: str
    inspiration: str
    functionality: str
    architecture: str
    technologiesUsed: str
    challengesFaced: str
    lessonsLearned: str
    nextSteps: str
    inPersonProject: Optional[bool] = True
    requiresPowerOutlet: Optional[bool] = False


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    prizes_attempted: "List[Prize]"
    prizes_won: "List[Prize]"

    class Config:
        orm_mode = True

from src.utility.schemas.Prize import Prize  # noqa
Project.update_forward_refs()
