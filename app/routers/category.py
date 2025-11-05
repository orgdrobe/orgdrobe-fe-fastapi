from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, oauth2

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["categories"],
    prefix="/categories"
)

@router.get("/master/", response_model=list[schemas.CategoryMasterResponse])
async def master_categories_all(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return db.query(models.CategoryMaster).all()

@router.get("/master/{id}", response_model=schemas.CategoryMasterResponse)
async def master_category_by_id(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    item = db.query(models.CategoryMaster).filter(models.CategoryMaster.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item

@router.get("/sub/", response_model=list[schemas.CategorySubResponse])
async def sub_categories_all(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return db.query(models.CategorySub).all()

@router.get("/sub/{id}", response_model=schemas.CategorySubResponse)
async def sub_category_by_id(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    item = db.query(models.CategorySub).filter(models.CategorySub.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item
