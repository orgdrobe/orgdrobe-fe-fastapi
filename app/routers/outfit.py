from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy import func, and_, not_, exists
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

@router.post(
    "/generate/random/garments", 
    response_model=list[schemas.GarmentResponse]
)
async def create_random_garments_for_outfit(
    params: schemas.CreateRandomOutfitParams, 
    db: db_dependency, 
    current_user: models.User = Depends(oauth2.get_current_user)
) -> list[schemas.GarmentResponse]:
    
    garments: list[schemas.GarmentResponse] = []
    
    for sub_category_id in params.category_sub_ids:
            
        query = db.query(models.Garment).filter(
            models.Garment.user_id == current_user.id,
            models.Garment.category_sub_id == sub_category_id
        )

        if params.gender_ids is not None and len(params.gender_ids) > 0:
            query = query.filter(models.Garment.gender_id.in_(params.gender_ids))

        random_garment = query.order_by(func.random()).first() # func.random() works for PostgreSQL and SQLite. for MySQL use func.rand()

        if random_garment:
            garments.append(random_garment)

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

@router.get("/{id}/garments/unused", response_model=list[schemas.GarmentResponse])
async def get_outfit_garments_unused(id: int, db: db_dependency, current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    outfit = db.query(models.Outfit).filter(models.Outfit.id == id).one()
    
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if outfit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    unused_garments = db.query(models.Garment).outerjoin(
        models.OutfitGarment,
        and_(
            models.Garment.id == models.OutfitGarment.garment_id,
            models.OutfitGarment.outfit_id == id
        )
    ).filter(
        models.Garment.user_id == current_user.id,
        models.OutfitGarment.garment_id == None
    ).all()
    
    return unused_garments

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

@router.put("/{id}/garments")
async def update_outfit_garments_by_ids(
    id: int, 
    garments_update: schemas.OutfitGarmentsUpdate,
    db: db_dependency, 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """Replace all garments in an outfit with new list (maintains order). (It delete all existing relationships for this outfit and then creates new relationships with order)"""
    
    outfit = db.query(models.Outfit).filter(models.Outfit.id == id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    if outfit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    garments = db.query(models.Garment).filter(
        models.Garment.id.in_(garments_update.garment_ids)
    ).all()
    
    if len(garments) != len(garments_update.garment_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more garments not found")
    
    for garment in garments:
        if garment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own all these garments")
    
    db.query(models.OutfitGarment).filter(
        models.OutfitGarment.outfit_id == id
    ).delete()
    
    for order, garment_id in enumerate(garments_update.garment_ids):
        outfit_garment = models.OutfitGarment(
            outfit_id=id,
            garment_id=garment_id,
            order=order
        )
        db.add(outfit_garment)
    
    db.commit()
    db.refresh(outfit)

    return {"message": f"Outfit {id} updated successfully"}

@router.post("/{outfit_id}/garments/{garment_id}", status_code=status.HTTP_201_CREATED)
async def add_garment_to_outfit(outfit_id: int, garment_id: int, db: db_dependency, current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    
    garment = db.query(models.Garment).filter(models.Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")
    
    if outfit.user_id != current_user.id or garment.user_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    existing = db.query(models.OutfitGarment).filter(
        models.OutfitGarment.outfit_id == outfit_id,
        models.OutfitGarment.garment_id == garment_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Garment already in outfit")

    max_order_result = db.query(func.max(models.OutfitGarment.order)).filter(
        models.OutfitGarment.outfit_id == outfit_id
    ).scalar()
    next_order = 0 if max_order_result is None else max_order_result + 1
    
    outfit_garment = models.OutfitGarment(
        outfit_id=outfit_id,
        garment_id=garment_id,
        order=next_order
    )
    db.add(outfit_garment)
    db.commit()
    
    return {"message": f"Garment {garment_id} added to outfit {outfit_id} successfully"}

@router.delete("/{outfit_id}/garments/{garment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garment_from_outfit(outfit_id: int, garment_id: int, db: db_dependency, current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    
    garment = db.query(models.Garment).filter(models.Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")
    
    if outfit.user_id != current_user.id or garment.user_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    outfit_garment = db.query(models.OutfitGarment).filter(
        models.OutfitGarment.outfit_id == outfit_id,
        models.OutfitGarment.garment_id == garment_id
    ).first()
    if not outfit_garment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Garment is not in this outfit")
    
    db.delete(outfit_garment)
    db.commit()

    return {"message": f"Garment {garment_id} deleted from outfit {outfit_id} successfully"}