from typing import List
from datetime import timedelta
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from db import schemas, crud
from db.data_base import get_db
from auth.handler import create_jwt_token, get_refresh_token, credentials_exception
from auth.handler import get_jwt_user, pwd_context

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


def authenticate_user(db, email: str, password: str):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise credentials_exception
    if not pwd_context.verify(password, user.hashed_password):
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="User is not active"
        )
    return user


@router.post("/auth/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    access_token_data: dict = {"sub": user.public_id}
    if user.is_admin:
        access_token_data.update({"admin": True})
    access_token = create_jwt_token(access_token_data, timedelta(minutes=15), "access")

    jwt_id = crud.create_token_id(db, user.public_id)
    refresh_token_data: dict = {"sub": user.public_id, "jti": jwt_id}
    refresh_token = create_jwt_token(refresh_token_data, timedelta(days=30), "refresh")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/auth/refresh", response_model=schemas.Token)
async def refresh_access_token(token: dict = Depends(get_refresh_token),
                               db: Session = Depends(get_db)):
    public_id: str = token.get("sub")
    user = crud.get_app_user(db, public_id)

    jti: str = token.get("jti")
    if not crud.validate_refresh_token(db, jti, public_id):
        raise credentials_exception("Invalid refresh token")

    data: dict = {"sub": user.public_id}
    access_token = create_jwt_token(data, timedelta(minutes=15), "access")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=schemas.UserApp)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    return user


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100,
               public_id: str = Depends(get_jwt_user),
               db: Session = Depends(get_db)):

    app_user = crud.get_app_user(db, public_id)
    if app_user is None or not app_user.is_admin:
        raise credentials_exception("Not administrator")

    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int,
              public_id: str = Depends(get_jwt_user),
              db: Session = Depends(get_db)):

    app_user = crud.get_app_user(db, public_id=public_id)
    if app_user is None:
        raise credentials_exception("Missing/suspended account")

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate,
        db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)
