from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.routers.auth import current_user_admin, current_user_participant, current_user_organizer
from src.utility.database import models
from src.utility.database.database import get_db
from src.utility.responses import MentorshipRequestNotFoundException, UserNotFoundException, CredentialException, \
    PrizeNotFoundException
from src.utility.schemas.MentorshipRequest import MentorshipRequestCreate
from src.utility.schemas.MentorshipRequest import MentorshipRequest
from src.utility.schemas.User import User

mentorship_request_router = APIRouter()


def load_mentorship_request_from_id(mentorship_request_id: int, db: Session = Depends(get_db)):
    mentorship_request = db.query(models.MentorshipRequestModel).filter(
        models.MentorshipRequestModel.id == mentorship_request_id).first()

    if mentorship_request is None:
        raise MentorshipRequestNotFoundException

    return mentorship_request


# -------------------------------------------------------------------------------
#
#           MentorshipRequest Create, Read, Update, Destroy Endpoints
#
# -------------------------------------------------------------------------------

@mentorship_request_router.get("/all", response_model=List[MentorshipRequest],
                               dependencies=[Depends(current_user_organizer)])
async def get_all_mentorship_requests(
        db: Session = Depends(get_db),
):
    return db.query(models.MentorshipRequestModel).all()


@mentorship_request_router.get("/{mentorship_request_id}", response_model=MentorshipRequest)
async def get_mentorship_request(current_user: User = Depends(current_user_participant),
                                 mentorship_request: MentorshipRequest = Depends(load_mentorship_request_from_id)):
    all_user_requests = [request.id for request in current_user.mentorship_requests_participant]
    if current_user.role.name == 'participant' and mentorship_request.id not in all_user_requests:
        return CredentialException()

    return mentorship_request


@mentorship_request_router.post("/new", response_model=MentorshipRequest, status_code=201)
def create_mentorship_request(
        mentorship_request: MentorshipRequestCreate,
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db)
):
    u: User = db.query(models.UserModel).filter(models.UserModel.id == current_user.id).first()
    if u.mentorship_request is not None:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "You are already assigned to a mentorship_request. Please delete the mentorship_request or leave the mentorship_request "
                          "team if you wish to create a new one."
            },
        )

    new_mentorship_request = models.MentorshipRequestModel(**mentorship_request.dict())
    db.add(new_mentorship_request)
    db.commit()
    db.refresh(new_mentorship_request)

    # Assign new mentorship_request to user
    db.query(models.UserModel).filter(models.UserModel.id == current_user.id).update(
        {'mentorship_request_id': new_mentorship_request.id})
    db.commit()

    return new_mentorship_request


@mentorship_request_router.delete("/{mentorship_request_id}")
async def delete_mentorship_request(
        mentorship_request_id: int,
        mentorship_request: MentorshipRequest = Depends(load_mentorship_request_from_id),
        current_user: User = Depends(current_user_participant),
        db: Session = Depends(get_db)
):
    if current_user.role.name == 'participant' and mentorship_request.participant_user_id != current_user.id:
        return CredentialException()

    db.delete(mentorship_request)
    db.commit()

    return {
        "detail": "MentorshipRequest successfully deleted.",
        "mentorship_request_id": mentorship_request_id
    }


@mentorship_request_router.put("/{mentorship_request_id}",
                               dependencies=[Depends(load_mentorship_request_from_id)],
                               response_model=MentorshipRequest
                               )
def update_mentorship_request(
        mentorship_request_id: int,
        mentorship_request: MentorshipRequestCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(current_user_participant),
):
    all_user_requests = [request.id for request in current_user.mentorship_requests_participant]
    if current_user.role.name == 'participant' and mentorship_request_id not in all_user_requests:
        return CredentialException()

    db.query(models.MentorshipRequestModel).filter(models.MentorshipRequestModel.id == mentorship_request_id).update(
        {**mentorship_request.dict()})
    db.commit()

    return load_mentorship_request_from_id(mentorship_request_id, db)


# -------------------------------------------------------------------------------
#
#           User Assignment and Unassignment
#
# -------------------------------------------------------------------------------


@mentorship_request_router.post("/{mentorship_request_id}/set_participant/{user_id}", response_model=MentorshipRequest,
                                dependencies=[Depends(current_user_organizer)])
async def add_participant_to_request(
        user_id: int,
        mentorship_request: MentorshipRequest = Depends(load_mentorship_request_from_id),
        db: Session = Depends(get_db)
):
    if mentorship_request is None:
        raise MentorshipRequestNotFoundException

    mentorship_request.participant_user_id = user_id
    db.add(mentorship_request)
    db.commit()
    db.refresh(mentorship_request)

    return mentorship_request


@mentorship_request_router.post("/{mentorship_request_id}/set_mentor/{user_id}", response_model=MentorshipRequest,
                                dependencies=[Depends(current_user_organizer)])
async def add_participant_to_request(
        user_id: int,
        mentorship_request: MentorshipRequest = Depends(load_mentorship_request_from_id),
        db: Session = Depends(get_db)
):
    if mentorship_request is None:
        raise MentorshipRequestNotFoundException

    mentorship_request.mentor_user_id = user_id
    db.add(mentorship_request)
    db.commit()
    db.refresh(mentorship_request)

    return mentorship_request
