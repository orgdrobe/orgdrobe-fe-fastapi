from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, oauth2

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["genders"],
    prefix="/genders"
)

@router.get("/", response_model=list[schemas.GenderResponse])
async def genders_all(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return db.query(models.Gender).all()

@router.get("/{id}", response_model=schemas.GenderResponse)
async def gender_by_id(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    item = db.query(models.Gender).filter(models.Gender.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item