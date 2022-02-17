from sqlalchemy.orm import Session

from src.utility.database import models
from src.utility.schemas.User import UserCreate


def get_user_by_id_db(db: Session, user_id: int):
    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()


def get_user_by_email_db(db: Session, email: str):
    return db.query(models.UserModel).filter(models.UserModel.email == email).first()


def create_user_db(db: Session, user: UserCreate):
    db_user = models.UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
