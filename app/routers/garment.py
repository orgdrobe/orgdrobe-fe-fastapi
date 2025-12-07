from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated
import base64, binascii

from ..database import get_db
from .. import models, schemas, utils, oauth2
from ..ml.garment_classify import garment_classify
from ..ml import garment_embeddings
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

@router.get("/embeddings/check", response_model=schemas.GarmentEmbeddingsCheckResponse)
async def check_garment_embeddings_status(
    db: db_dependency,
    current_user: models.User = Depends(oauth2.get_current_user)
):

    total_garments = db.query(models.Garment).filter(
        models.Garment.user_id == current_user.id
    ).count()

    processed_garments = db.query(models.GarmentEmbeddings).join(
        models.Garment,
        models.GarmentEmbeddings.garment_id == models.Garment.id
    ).filter(
        models.Garment.user_id == current_user.id
    ).count()

    return {
        "total": total_garments,
        "processed": processed_garments,
        "unprocessed": total_garments - processed_garments
    }

@router.post("/embeddings", response_model=schemas.GarmentEmbeddingsCreateStatsResponse)
async def create_garment_embeddings(
    db: db_dependency, 
    force_rewrite: bool = False,
    current_user: models.User = Depends(oauth2.get_current_user)
):
    stats = garment_embeddings.process_user_garments_embeddings(
        user_id=current_user.id,
        db=db,
        force_recreate=force_rewrite
    )

    return stats

@router.get("/count", response_model=int)
async def get_garments_count(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)
):
    garment_count = db.query(models.Garment).filter(models.Garment.user_id == current_user.id).count()
    return garment_count

@router.post(
    "/filter",
    response_model=list[schemas.GarmentResponse])
async def filter_garments(
    params: schemas.FilterGarmentsByParams,
    db: db_dependency,
    current_user: models.User = Depends(oauth2.get_current_user)
):
    query = db.query(models.Garment).filter(models.Garment.user_id == current_user.id)

    if params.gender_ids:
        query = query.filter(models.Garment.gender_id.in_(params.gender_ids))
        
    if params.category_master_ids:
        query = query.filter(models.Garment.category_master_id.in_(params.category_master_ids))
        
    if params.category_sub_ids:
        query = query.filter(models.Garment.category_sub_id.in_(params.category_sub_ids))
        
    if params.season_ids:
        query = query.filter(models.Garment.season_id.in_(params.season_ids))
        
    if params.usage_ids:
        query = query.filter(models.Garment.usage_id.in_(params.usage_ids))
        
    if params.color_ids:
        query = query.filter(models.Garment.color_id.in_(params.color_ids))
        
    if params.garment_type_ids:
        query = query.filter(models.Garment.garment_type_id.in_(params.garment_type_ids))

    return query.all()

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

        db.query(models.GarmentEmbeddings).filter(
            models.GarmentEmbeddings.garment_id == id
        ).delete()
        
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