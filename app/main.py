from fastapi import APIRouter, FastAPI, HTTPException, Depends 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import Annotated, List

# from my files
from .database import engine, get_db
from . import models
from . import schemas
from . import hashing
from . import utils

app = FastAPI(
    title="Wardrobe FastAPI",
    description="by Maksym Stepanuik for Uni",
    version="0.0.1",
    docs_url="/docs"
) # Create the FastAPI instance

models.Base.metadata.create_all(bind=engine) # Create the tables

db_dependency = Annotated[Session, Depends(get_db)] # dependency injection

# FastAPI routes

@app.get("/")
async def root():
    return {"openapi swagger":"http://127.0.0.1:8000/docs", "redoc":"http://127.0.0.1:8000/redoc"}

garments_router = APIRouter(tags=["garments"])

@garments_router.post("/garments", response_model=schemas.GarmentResponse)
async def create_garment(garment_in: schemas.GarmentCreate, db: db_dependency):
    garment = models.Garment(**garment_in.dict())
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment

@garments_router.get("/garments", response_model=List[schemas.GarmentResponse])
async def list_garments(db: db_dependency):
    garment_list = db.query(models.Garment).all()
    return garment_list

@garments_router.get("/garments/{id}", response_model=schemas.GarmentResponse)
async def read_garment(id: int, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Garment not found")

@garments_router.put("/garments/{id}", response_model=schemas.GarmentResponse)
async def update_garment(id: int, garment_in: schemas.GarmentBase, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == id).one()
        utils.update_object_attributes(garment_in, garment)
        db.commit()
        db.refresh(garment)
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"User {id} not found")

@garments_router.delete("/garments/{id}")
async def delete_garment(id: int, db: db_dependency):
    try:
        user = db.query(models.Garment).filter(models.Garment.id == id).one()
        db.delete(user)
        db.commit()
        return {"message": f"Garment {id} deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Garment {id} not found")

app.include_router(garments_router)

users_router = APIRouter(tags=["users"])

@users_router.post("/users", response_model=schemas.UserResponse)
async def create_user(user_in: schemas.UserCreate, db: db_dependency):
    hashed = hashing.get_password_hash(user_in.password)
    user_in.password = hashed
    user = models.User(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@users_router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(db: db_dependency):
    user_list = db.query(models.User).all()
    return user_list

# @users_router.get("/users/me") # TODO
# async def get_current_user():
#     return {"Message": "this is the current user"}

@users_router.get("/users/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

@users_router.put("/users/{id}", response_model=schemas.UserResponse)
async def update_user(id: int, user_in: schemas.UserBase, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        utils.update_object_attributes(user_in, user)
        db.commit()
        db.refresh(user)
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@users_router.delete("/users/{id}")
def delete_user(id: int, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

app.include_router(users_router)
