from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.routers.auth import current_user_admin
from src.utility.database import models
from src.utility.database.database import get_db
from src.utility.responses import RoleNotFoundException, UserNotFoundException
from src.utility.schemas.Role import RoleCreate
from src.utility.schemas.Role import Role
from src.utility.schemas.User import User

role_router = APIRouter()


def load_role_from_id(role_id: int, db: Session = Depends(get_db)):
    role = db.query(models.RoleModel).filter(models.RoleModel.id == role_id).first()

    if role is None:
        raise RoleNotFoundException

    return role


# -------------------------------------------------------------------------------
#
#           Role Create, Read, Update, Destroy Endpoints
#
# -------------------------------------------------------------------------------

@role_router.get("/all", response_model=List[Role], dependencies=[Depends(current_user_admin)])
async def get_all_roles(
        db: Session = Depends(get_db),
):
    return db.query(models.RoleModel).all()


@role_router.get("/{role_id}", response_model=Role)
async def get_role(current_user: User = Depends(current_user_admin),
                   role: Role = Depends(load_role_from_id)):
    return role


@role_router.post("/new", response_model=Role)
async def create_role(role: RoleCreate, current_user: User = Depends(current_user_admin),
                      db: Session = Depends(get_db)):
    new_role = models.RoleModel(**role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@role_router.delete("/{role_id}")
async def delete_role(
        role_id: int,
        role: Role = Depends(load_role_from_id),
        current_user: User = Depends(current_user_admin),
        db: Session = Depends(get_db)
):
    db.delete(role)
    db.commit()

    return {
        "detail": "Role successfully deleted.",
        "role_id": role_id
    }


@role_router.put("/{role_id}",
                 dependencies=[Depends(load_role_from_id)],
                 response_model=Role
                 )
def update_role(
        role_id: int,
        role: RoleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(current_user_admin),
):
    db.query(models.RoleModel).filter(models.RoleModel.id == role_id).update({**role.dict()})
    db.commit()

    return load_role_from_id(role_id, db)


# Role Assignment
@role_router.post("/{role_id}/assign/{user_id}", response_model=User, dependencies=[Depends(current_user_admin)])
def assign_user_to_role(
        role_id: int,
        user_id: int,
        db: Session = Depends(get_db),
):

    u = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if not u:
        return UserNotFoundException()

    db.query(models.UserModel).filter(models.UserModel.id == user_id).update({'role_id': role_id})
    db.commit()

    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()


@role_router.post("/unassign/{user_id}", response_model=User, dependencies=[Depends(current_user_admin)])
def remove_user_roles(user_id: int, db: Session = Depends(get_db)):

    db.query(models.UserModel).filter(models.UserModel.id == user_id).update({'role_id': None})
    db.commit()

    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
