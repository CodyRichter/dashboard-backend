from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.routers.auth import current_user_admin, current_user_participant, current_user_organizer
from src.utility.database import models
from src.utility.database.database import get_db
from src.utility.responses import ProjectNotFoundException, UserNotFoundException, CredentialException, \
    PrizeNotFoundException
from src.utility.schemas.Project import ProjectCreate
from src.utility.schemas.Project import Project
from src.utility.schemas.User import User


project_router = APIRouter()


def load_project_from_id(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.ProjectModel).filter(models.ProjectModel.id == project_id).first()

    if project is None:
        raise ProjectNotFoundException

    return project


# -------------------------------------------------------------------------------
#
#           Project Create, Read, Update, Destroy Endpoints
#
# -------------------------------------------------------------------------------

@project_router.get("/all", response_model=List[Project], dependencies=[Depends(current_user_organizer)])
async def get_all_projects(
        db: Session = Depends(get_db),
):
    return db.query(models.ProjectModel).all()


@project_router.get("/{project_id}", response_model=Project)
async def get_project(current_user: User = Depends(current_user_participant),
                      project: Project = Depends(load_project_from_id)):
    # Ensure that users can only view their own projects
    if current_user.role.name == 'participant':
        if not current_user.project or project.id != current_user.project.id:
            return CredentialException()

    return project


@project_router.post("/new", response_model=Project, status_code=201)
def create_project(
        project: ProjectCreate,
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db)
):
    u: User = db.query(models.UserModel).filter(models.UserModel.id == current_user.id).first()
    if u.project is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "You are already assigned to a project. Please delete the project or leave the project "
                          "team if you wish to create a new one."
            },
        )

    new_project = models.ProjectModel(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Assign new project to user
    db.query(models.UserModel).filter(models.UserModel.id == current_user.id).update({'project_id': new_project.id})
    db.commit()

    return new_project


@project_router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        project: Project = Depends(load_project_from_id),
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db)
):

    if current_user.role.name == 'participant':
        if not current_user.project or project_id != current_user.project.id:
            return CredentialException()

    db.delete(project)
    db.commit()

    return {
        "detail": "Project successfully deleted.",
        "project_id": project_id
    }


@project_router.put("/{project_id}",
                    dependencies=[Depends(load_project_from_id)],
                    response_model=Project
                    )
def update_project(
        project_id: int,
        project: ProjectCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(current_user_participant),
):

    if current_user.role.name == 'participant':
        if not current_user.project or project_id != current_user.project.id:
            return CredentialException()

    db.query(models.ProjectModel).filter(models.ProjectModel.id == project_id).update({**project.dict()})
    db.commit()

    return load_project_from_id(project_id, db)


# -------------------------------------------------------------------------------
#
#           User Assignment and Unassignment
#
# -------------------------------------------------------------------------------


@project_router.post("/{project_id}/add_user/{user_id}", response_model=Project)
def assign_user_to_project(
        project_id: int,
        user_id: int,
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db),
):
    user_to_assign: User = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if not user_to_assign:
        return UserNotFoundException()

    if current_user.role.name == 'participant':
        if not current_user.project or project_id != current_user.project.id:
            return CredentialException()

    if user_to_assign.project:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Unable to add target user to project as are already assigned to one. "
                          "They must either leave that project or delete it before they can be added to another."
            },
        )

    db.query(models.UserModel).filter(models.UserModel.id == user_id).update({'project_id': project_id})
    db.commit()

    return db.query(models.ProjectModel).filter(models.ProjectModel.id == project_id).first()


@project_router.post("/remove_user/{user_id}", response_model=User)
def remove_user_from_project(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(current_user_participant)
):
    # Ensure that participants can only remove their self
    if current_user.role.name == 'participant' and user_id != current_user.id:
        raise CredentialException()

    db.query(models.UserModel).filter(models.UserModel.id == user_id).update({'project_id': None})
    db.commit()

    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()


@project_router.post("/{project_id}/attempt_prizes", response_model=Project)
async def attempt_prizes(
        project_id: int,
        attempted_prizes: List[int],
        project: Project = Depends(load_project_from_id),
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db)
):

    if project is None:
        raise ProjectNotFoundException

    # Only allow participants to modify their own project
    if current_user.role == 'participant' and current_user.project != project_id:
        raise CredentialException()

    project.prizes_attempted = []

    for prize_id in attempted_prizes:
        prize = db.query(models.PrizeModel).filter(models.PrizeModel.id == prize_id).first()

        if not prize:
            raise PrizeNotFoundException()

        project.prizes_attempted.append(prize)
        db.add(project)

    db.commit()
    db.refresh(project)

    return project
