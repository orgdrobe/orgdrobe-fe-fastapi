from fastapi import APIRouter, FastAPI, HTTPException, Depends 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import Annotated, List

# from my files
from .database import engine, get_db
from . import models
from .routers import user, garment

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

app.include_router(garment.router)
app.include_router(user.router)
