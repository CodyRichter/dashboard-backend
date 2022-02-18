from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.routers.auth import get_current_active_user, current_user_organizer
from src.utility.database import models
from src.utility.database.database import get_db
from src.utility.responses import PrizeNotFoundException, ProjectNotFoundException
from src.utility.schemas.Prize import Prize, PrizeCreate
from src.utility.schemas.Project import Project
from src.utility.schemas.User import User

prize_router = APIRouter()


def load_prize_from_id(prize_id: int, db: Session = Depends(get_db)):
    prize = db.query(models.PrizeModel).filter(models.PrizeModel.id == prize_id).first()

    if prize is None:
        raise PrizeNotFoundException

    return prize


# -------------------------------------------------------------------------------
#
#           Prize Create, Read, Update, Destroy Endpoints
#
# -------------------------------------------------------------------------------

@prize_router.get("/all", response_model=List[Prize])
async def get_all_prizes(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(models.PrizeModel).all()


@prize_router.get("/{prize_id}", response_model=Prize)
async def get_prize(current_user: User = Depends(get_current_active_user),
                    prize: Prize = Depends(load_prize_from_id)):
    return prize


@prize_router.post("/new", response_model=Prize, status_code=201)
async def create_prize(prize: PrizeCreate, current_user: User = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):
    new_prize = models.PrizeModel(**prize.dict())
    db.add(new_prize)
    db.commit()
    db.refresh(new_prize)
    return new_prize


@prize_router.delete("/{prize_id}")
async def delete_prize(
        prize_id: int,
        prize: Prize = Depends(load_prize_from_id),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    db.delete(prize)
    db.commit()

    return {
        "detail": "Prize successfully deleted.",
        "prize_id": prize_id
    }


@prize_router.put("/{prize_id}", dependencies=[Depends(load_prize_from_id)], response_model=Prize)
def update_prize(
        prize_id: int,
        prize: PrizeCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    db.query(models.PrizeModel).filter(models.PrizeModel.id == prize_id).update({**prize.dict()})
    db.commit()

    return load_prize_from_id(prize_id, db)


# -------------------------------------------------------------------------------
#
#           Prize Winner Assignment and Removal Endpoints
#
# -------------------------------------------------------------------------------


@prize_router.post("/{prize_id}/winner/{project_id}", response_model=Prize)
async def assign_winner_to_prize(
        prize_id: int,
        project_id: int,
        prize: Prize = Depends(load_prize_from_id),
        current_user: User = Depends(current_user_organizer),
        db: Session = Depends(get_db)
):
    project: Project = db.query(models.ProjectModel).filter(models.ProjectModel.id == project_id).first()

    if project is None:
        raise ProjectNotFoundException

    project.prizes_won.append(prize)
    db.add(project)
    db.commit()

    return prize


@prize_router.delete("/{prize_id}/winner/{project_id}", response_model=Prize)
async def remove_winner_from_prize(
        prize_id: int,
        project_id: int,
        prize: Prize = Depends(load_prize_from_id),
        current_user: User = Depends(current_user_organizer),
        db: Session = Depends(get_db)
):
    project: Project = db.query(models.ProjectModel).filter(models.ProjectModel.id == project_id).first()

    if project is None:
        raise ProjectNotFoundException

    project.prizes_won.remove(prize)
    db.add(project)
    db.commit()

    return prize
