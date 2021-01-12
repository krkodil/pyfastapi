from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db import schemas, crud
from db.data_base import get_db

router = APIRouter()


@router.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
