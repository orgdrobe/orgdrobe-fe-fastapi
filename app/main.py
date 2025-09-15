from fastapi import FastAPI, HTTPException, Depends 
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

@app.post("/garments/", response_model=schemas.GarmentResponse)
async def create_garment(garment_in: schemas.GarmentCreate, db: db_dependency):
    garment = models.Garment(**garment_in.dict())
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment

@app.get("/garments", response_model=List[schemas.GarmentResponse])
async def list_garments(db: db_dependency):
    garment_list = db.query(models.Garment).all()
    return garment_list

@app.get("/garments/{garment_id}", response_model=schemas.GarmentResponse)
async def read_garment(garment_id: int, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == garment_id).one()
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Garment not found")

@app.put("/garments/{garment_id}", response_model=schemas.GarmentResponse)
async def update_garment(garment_id: int, garment_in: schemas.GarmentBase, db: db_dependency):
    try:
        garment = db.query(models.Garment).filter(models.Garment.id == garment_id).one()
        utils.update_object_attributes(garment_in, garment)
        db.commit()
        db.refresh(garment)
        return garment
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"User {garment_id} not found")

@app.delete("/garments/{garment_id}")
async def delete_garment(garment_id: int, db: db_dependency):
    try:
        user = db.query(models.Garment).filter(models.Garment.id == garment_id).one()
        db.delete(user)
        db.commit()
        return {"message": f"Garment {garment_id} deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Garment {garment_id} not found")

@app.post("/users", response_model=schemas.UserResponse)
async def create_user(user_in: schemas.UserCreate, db: db_dependency):
    hashed = hashing.get_password_hash(user_in.password)
    user_in.password = hashed
    user = models.User(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users", response_model=List[schemas.UserResponse])
async def list_users(db: db_dependency):
    user_list = db.query(models.User).all()
    return user_list

# @app.get("/users/me") # TODO
# async def get_current_user():
#     return {"Message": "this is the current user"}

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user_in: schemas.UserBase, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).one()
        utils.update_object_attributes(user_in, user)
        db.commit()
        db.refresh(user)
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).one()
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")
