from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db import crud
from db.data_base import get_db

router = APIRouter()


@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}


@router.delete("/tokens")
def purge_all_refresh_tokens(db: Session = Depends(get_db)):
    count: int = crud.purge_refresh_tokens(db)
    return {"message": "Tokens deleted: " + str(count)}
