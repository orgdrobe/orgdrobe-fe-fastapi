from fastapi import APIRouter, HTTPException, Depends, status 
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
async def list_garments(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    garment_list = db.query(models.Garment).filter(models.Garment.user_id == current_user.id).all()
    return garment_list

@router.get("/{id}", response_model=schemas.GarmentResponse)
async def read_garment(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        
        if garment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Garment not found")

@router.put("/{id}", response_model=schemas.GarmentResponse)
async def update_garment(id: int, garment_in: schemas.GarmentCreate, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()

        if garment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

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

@router.get("/{id}/outfits", response_model=list[schemas.OutfitResponse])
async def get_garment_outfits(id: int, db: db_dependency, current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    garment = db.query(models.Garment).filter(models.Garment.id == id).first()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if garment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    outfits = db.query(models.Outfit).join(
        models.OutfitGarment,
        models.Outfit.id == models.OutfitGarment.outfit_id
    ).filter(
        models.OutfitGarment.garment_id == id
    ).all()
    
    return outfits