from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated
import base64, binascii

from ..database import get_db
from .. import models, schemas, utils, oauth2
from ..ml.garment_classify import garment_classify
from app.schemas import GarmentClassify

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

@router.post("/classify", response_model=schemas.GarmentClassify)
async def classify_garment_from_image(
    db: db_dependency, 
    image_file: UploadFile = File(None), 
    base64_str: str = Form(None),
    current_user: models.User = Depends(dependency=oauth2.get_current_user)
) -> GarmentClassify:

    """
    Don't send empty value(s) (don't enable the checkbox the send empty value in swagger)
    """
    
    image_bytes = None

    if image_file:
        image_bytes = await image_file.read()
    
    elif base64_str:
        try:
            # Remove header if present (e.g., "data:image/jpeg;base64,...")
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]
            
            image_bytes = base64.b64decode(base64_str)
        except binascii.Error:
            raise HTTPException(status_code=400, detail="Invalid Base64 string")
    
    else:
        raise HTTPException(
            status_code=400, 
            detail="No image provided. Upload a file or provide a base64_str form field."
        )

    garment_info = garment_classify(image_bytes, db)
    return garment_info

@router.get("/count", response_model=int)
async def get_garments_count(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)
):
    garment_count = db.query(models.Garment).filter(models.Garment.user_id == current_user.id).count()
    return garment_count

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