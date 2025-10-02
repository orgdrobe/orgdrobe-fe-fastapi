from fastapi import APIRouter, HTTPException, Depends 
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, utils, oauth2

db_dependency = Annotated[Session, Depends(get_db)] # dependency injection

router = APIRouter(
    tags=["garments"],
    prefix="/garments"
)

@router.post("/", response_model=schemas.GarmentResponse)
async def create_garment(garment_in: schemas.GarmentCreate, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    garment = models.Garment(**garment_in.dict(), user_id = current_user.id)
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment

@router.get("/", response_model=list[schemas.GarmentResponse])
async def list_garments(db: db_dependency):
    garment_list = db.query(models.Garment).all()
    return garment_list

@router.get("/{id}", response_model=schemas.GarmentResponse)
async def read_garment(id: int, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Garment not found")

@router.put("/{id}", response_model=schemas.GarmentResponse)
async def update_garment(id: int, garment_in: schemas.GarmentBase, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        utils.update_object_attributes(garment_in, garment)
        db.commit()
        db.refresh(garment)
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.delete("/{id}")
async def delete_garment(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()

        if garment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        db.delete(garment)
        db.commit()
        return {"message": f"Garment {id} deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Garment {id} not found")