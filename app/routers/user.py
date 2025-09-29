from fastapi import APIRouter,  HTTPException, Depends 
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

@router.get("/", response_model=list[schemas.UserResponse])
async def list_users(db: db_dependency, current_user: int = Depends(oauth2.get_current_user)):
    user_list = db.query(models.User).all()
    return user_list

# @users_router.get("/users/me") # TODO
# async def get_current_user():
#     return {"Message": "this is the current user"}

@router.get("/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: db_dependency, current_user: int = Depends(oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/{id}", response_model=schemas.UserResponse)
async def update_user(id: int, user_in: schemas.UserBase, db: db_dependency, current_user: int = Depends(oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        utils.update_object_attributes(user_in, user)
        db.commit()
        db.refresh(user)
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{id}")
def delete_user(id: int, db: db_dependency, current_user: int = Depends(oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")