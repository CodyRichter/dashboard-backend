from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship

from src.utility.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

    # Authentication and Security
    password = Column(String)
    password_reset_token = Column(String)
    password_reset_token_sent_at = Column(DateTime)

    # Permissions
    disabled = Column(Boolean, default=False)
    role = relationship("RoleModel", back_populates="users")
    role_id = Column(Integer, ForeignKey("roles.id"))

    # Project
    project = relationship("ProjectModel", back_populates="users")
    project_id = Column(Integer, ForeignKey("projects.id"))

    # Mentorship Requests
    mentorship_requests_participant = relationship(
        "MentorshipRequestModel",
        back_populates="participant_user",
        foreign_keys='MentorshipRequestModel.participant_user_id'
    )
    mentorship_requests_mentor = relationship(
        "MentorshipRequestModel",
        back_populates="mentor_user",
        foreign_keys='MentorshipRequestModel.mentor_user_id'
    )


prize_project_winner_association = Table('prize_project_winner_association', Base.metadata,
                                         Column('project_id', ForeignKey('projects.id')),
                                         Column('prize_id', ForeignKey('prizes.id'))
                                         )

prize_project_attempt_association = Table('prize_project_attempt_association', Base.metadata,
                                          Column('project_id', ForeignKey('projects.id')),
                                          Column('prize_id', ForeignKey('prizes.id'))
                                          )


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image_url = Column(String)
    github_link = Column(String)
    video_link = Column(String)
    description = Column(String, index=True)
    inspiration = Column(String)
    functionality = Column(String)
    architecture = Column(String)
    technologiesUsed = Column(String)
    challengesFaced = Column(String)
    lessonsLearned = Column(String)
    nextSteps = Column(String)
    inPersonProject = Column(Boolean, default=True)
    requiresPowerOutlet = Column(Boolean, default=False)

    users = relationship("UserModel", back_populates='project')
    prizes_attempted = relationship('PrizeModel', secondary=prize_project_attempt_association,
                                    back_populates='attempting_projects')
    prizes_won = relationship('PrizeModel', secondary=prize_project_winner_association,
                              back_populates='winning_projects')


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(String, index=True)

    users = relationship("UserModel", back_populates='role')


class MentorshipRequestModel(Base):
    __tablename__ = "mentorship_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    technology_used = Column(String)
    urgency = Column(Integer, index=True)
    image_url = Column(String)

    resolved = Column(Boolean, default=False)


    # User who made request
    participant_user_id = Column(Integer, ForeignKey('users.id'))
    participant_user = relationship(
        "UserModel",
        back_populates="mentorship_requests_participant",
        foreign_keys=[participant_user_id]
    )

    # User who is helping with the request
    mentor_user_id = Column(Integer, ForeignKey('users.id'))
    mentor_user = relationship(
        "UserModel",
        back_populates="mentorship_requests_mentor",
        foreign_keys=[mentor_user_id]
    )


class PrizeModel(Base):
    __tablename__ = "prizes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Best Hardware Hack
    description = Column(String, index=True)  # Create a hack using XYZ
    reward = Column(String, index=True)  # Nintendo Switch
    sponsor = Column(String, index=True, default="")  # HackathonXYZ
    priority = Column(Integer, index=True)  # Higher priority should appear first
    selectable = Column(Boolean, index=True)  # If projects can select the prize

    # Associations
    attempting_projects = relationship('ProjectModel', secondary=prize_project_attempt_association,
                                       back_populates='prizes_attempted')
    winning_projects = relationship('ProjectModel', secondary=prize_project_winner_association,
                                    back_populates='prizes_won')
