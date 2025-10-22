from fastapi import APIRouter,  HTTPException, Depends, status
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import models, schemas, hashing, utils, oauth2

db_dependency = Annotated[Session, Depends(get_db)] # dependency injection

router = APIRouter(
    tags=["users"],
    prefix="/users"
)

@router.post("/", response_model=schemas.UserResponse)
async def create_user(user_in: schemas.UserCreate, db: db_dependency):
    hashed = hashing.get_password_hash(user_in.password)
    user_in.password = hashed
    user = models.User(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=list[schemas.UserResponsePublic])
async def list_users(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    user_list = db.query(models.User).all()
    return user_list

@router.get("/users/me", response_model=schemas.UserResponse)
async def get_user_mylesf(db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user

@router.get("/{id}", response_model=schemas.UserResponsePublic)
async def get_user(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/{id}", response_model=schemas.UserResponse)
async def update_user(id: int, user_in: schemas.UserBase, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    hashed = hashing.get_password_hash(user_in.password)
    user_in.password = hashed
    try:
        user = db.query(models.User).filter(models.User.id == id).one()

        if user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        utils.update_object_attributes(user_in, user)
        db.commit()
        db.refresh(user)
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}")
def delete_user(id: int, db: db_dependency, current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()

        if user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")