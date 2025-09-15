from fastapi import APIRouter, HTTPException, Depends 
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated, List

from ..database import get_db
from .. import models, schemas, utils

db_dependency = Annotated[Session, Depends(get_db)] # dependency injection

router = APIRouter(tags=["garments"])

@router.post("/garments", response_model=schemas.GarmentResponse)
async def create_garment(garment_in: schemas.GarmentCreate, db: db_dependency):
    garment = models.Garment(**garment_in.dict())
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment

@router.get("/garments", response_model=List[schemas.GarmentResponse])
async def list_garments(db: db_dependency):
    garment_list = db.query(models.Garment).all()
    return garment_list

@router.get("/garments/{id}", response_model=schemas.GarmentResponse)
async def read_garment(id: int, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Garment not found")

@router.put("/garments/{id}", response_model=schemas.GarmentResponse)
async def update_garment(id: int, garment_in: schemas.GarmentBase, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        utils.update_object_attributes(garment_in, garment)
        db.commit()
        db.refresh(garment)
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.delete("/garments/{id}")
async def delete_garment(id: int, db: db_dependency):
    try:
        user = db.query(models.Garment).filter(models.Garment.id == id).one()
        db.delete(user)
        db.commit()
        return {"message": f"Garment {id} deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Garment {id} not found")