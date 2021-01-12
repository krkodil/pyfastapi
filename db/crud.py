from sqlalchemy.orm import Session
import uuid

from db import models, schemas
from auth.handler import pwd_context


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_app_user(db: Session, public_id: str):
    return db.query(models.User)\
        .filter(models.User.public_id == public_id) \
        .filter(models.User.is_active) \
        .first()


def create_token_id(db: Session, public_id: str):
    jti: str = str(uuid.uuid1())
    refresh_token = db.query(models.RefreshToken).filter(models.RefreshToken.public_id == public_id).first()
    if refresh_token is None:
        refresh_token = models.RefreshToken(jti=jti, public_id=public_id)
        db.add(refresh_token)
    else:
        refresh_token.jti = jti
    db.commit()
    return jti


def validate_refresh_token(db: Session, jti: str, public_id: str):
    db_refresh_token = db.query(models.RefreshToken).filter(models.RefreshToken.jti == jti).first()
    if db_refresh_token.is_blacklisted:
        return False
    else:
        return db_refresh_token.public_id == public_id


def purge_refresh_tokens(db: Session):
    return db.query(models.RefreshToken).delete()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db_user.public_id = uuid.uuid1()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
