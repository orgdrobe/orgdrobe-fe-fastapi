from fastapi import APIRouter, HTTPException, Depends, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, hashing, oauth2

db_dependency = Annotated[Session, Depends(get_db)]
router = APIRouter(
    tags=["auth"],
    prefix="/auth"
)

@router.post("/email")
async def login_email(db: db_dependency, credentials: OAuth2PasswordRequestForm = Depends()):
    try:
        user = db.query(models.User).filter(models.User.email == credentials.username).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    if not hashing.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer" } 