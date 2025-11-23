from sqlalchemy.orm import Session
from app import models
from app.auth_utils import hash_password


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, username: str, email: str, phone_number: str, password: str):
    hashed_password = hash_password(password)
    db_user = models.User(
        username=username,
        email=email,
        phone_number=phone_number,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: models.User, *, username: str | None = None, email: str | None = None, phone_number: str | None = None) -> models.User:
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if phone_number is not None:
        user.phone_number = phone_number
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
