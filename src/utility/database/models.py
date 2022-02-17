from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
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

    # Associations
    project_id = Column(Integer, ForeignKey("projects.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))


class PrizeProjectWinnerMapModel(Base):
    __tablename__ = 'prize_project_winner_map'
    id = Column(Integer, primary_key=True, index=True)
    projectId = Column(Integer, ForeignKey('projects.id'))
    prizeId = Column(Integer, ForeignKey('prizes.id'))


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String)
    github_link = Column(String)
    video_link = Column(String)

    prizes_won = relationship('PrizeModel', secondary='prize_project_winner_map', back_populates='winning_projects')


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    description = Column(String, index=True)

    users = relationship("UserModel", back_populates='role')


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
    winning_projects = relationship('ProjectModel', secondary='prize_project_winner_map', back_populates='prizes_won')
