from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, oauth2

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["seasons"],
    prefix="/seasons"
)

@router.get("/", response_model=list[schemas.SeasonResponse])
async def seasons_all(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return db.query(models.Season).all()

@router.get("/{id}", response_model=schemas.SeasonResponse)
async def season_by_id(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    item = db.query(models.Season).filter(models.Season.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item