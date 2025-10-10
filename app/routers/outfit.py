from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, utils, oauth2

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    tags=["outfits"],
    prefix="/outfits"
)

@router.post("/", response_model=schemas.OutfitResponse)
async def create_outfit(outfit: schemas.OutfitCreate, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    outfit = models.Outfit(**outfit.dict(), user_id = current_user.id)
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit

@router.get("/", response_model=list[schemas.OutfitResponse])
async def list_outfits(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    garments = db.query(models.Outfit).filter(models.Outfit.user_id == current_user.id).all()
    return garments

@router.get("/{id}", response_model=schemas.OutfitResponse)
async def read_outfit(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        outfit = db.query(models.Outfit).filter(models.Outfit.id == id).one()
        
        if outfit.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return outfit
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.put(path="/{id}", response_model=schemas.OutfitResponse)
async def update_outfit(id: int, outfit_in: schemas.OutfitCreate, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        outfit = db.query(models.Outfit).filter(models.Outfit.id == id).one()

        if outfit.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        utils.update_object_attributes(outfit_in, outfit)
        db.commit()
        db.refresh(outfit)
        return outfit
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.delete("/{id}")
async def delete_outfit(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        outfit = db.query(models.Outfit).filter(models.Outfit.id == id).one()

        if outfit.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        db.delete(outfit)
        db.commit()
        return {"message": f"Outfit {id} deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Garment {id} not found")

@router.get("/{id}/garments", response_model=list[schemas.GarmentResponse])
async def get_outfit_garments(id: int, db: db_dependency, current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    outfit = db.query(models.Outfit).filter(models.Outfit.id == id).one()
    
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if outfit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    garments = db.query(models.Garment).join(
        models.OutfitGarment,
        models.Garment.id == models.OutfitGarment.garment_id
    ).filter(
        models.OutfitGarment.outfit_id == id
    ).order_by(
        models.OutfitGarment.order
    ).all()
    
    return garments