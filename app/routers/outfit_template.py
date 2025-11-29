from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy import func, and_, not_, exists
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, utils, oauth2

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    tags=["outfit-templates"],
    prefix="/outfit-templates"
)

@router.get(
    "/", 
    response_model=list[schemas.OutfitTemplateResponse]
)
async def outfit_tepmlates_all(
    db: db_dependency,
    current_user: models.User = Depends(oauth2.get_current_user)
) -> schemas.OutfitTemplateResponse:
    return db.query(models.OutfitTemplate).all()


@router.get(
    "/parameters",
    response_model=list[schemas.OutfitTemplateParameterResponse]
)
async def outfit_tepmlates_parameters(
    db: db_dependency, 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    return db.query(models.OutfitTemplateParameter).all()


@router.get(
    "/{id}/parameters",
    response_model=list[schemas.OutfitTemplateParameterResponse]
)
async def outfit_tepmlate_parameters_by_template_id(
    id: int, 
    db: db_dependency, 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    params = db.query(
        models.OutfitTemplateParameter
    ).join(
        models.OutfitTemplate,
        models.OutfitTemplateParameter.outfit_template_id == models.OutfitTemplate.id 
    ).filter(
        models.OutfitTemplateParameter.outfit_template_id == id
    ).all()
    return params