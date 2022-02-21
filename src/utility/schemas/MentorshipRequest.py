from pydantic import BaseModel


class MentorshipRequestBase(BaseModel):
    title: str
    description: str
    technology_used: str
    urgency: int
    image_url: str


class MentorshipRequestCreate(MentorshipRequestBase):
    pass


class MentorshipRequest(MentorshipRequestBase):
    id: int
    resolved: bool = False

    participant_user_id: int
    mentor_user_id: int

    class Config:
        orm_mode = True
