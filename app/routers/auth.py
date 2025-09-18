from fastapi import APIRouter, HTTPException, Depends 
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, hashing

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["auth"],
    # prefix="/auth"
)

@router.post("/email")
async def login_email(credentials: schemas.UserEmailPassword, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.email == credentials.email).one()
    except NoResultFound:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not hashing.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    #TODO
    return {"token": "todo"} 