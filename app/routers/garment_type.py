from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, oauth2

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["types"],
    prefix="/types"
)

@router.get("/", response_model=list[schemas.TypeResponse])
async def types_all(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return db.query(models.Type).all()

@router.get("/{id}", response_model=schemas.TypeResponse)
async def type_by_id(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    item = db.query(models.Type).filter(models.Type.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item