from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated

# from my files
from .database import engine, get_db
from . import models
from .routers import user, garment, auth, outfit, image, gender, category, type, color, season, usage

app = FastAPI(
    title="Wardrobe FastAPI",
    description="by Maksym Stepanuik for Uni",
    version="0.0.1",
    docs_url="/docs"
) # Create the FastAPI instance


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine) # Create the tables

db_dependency = Annotated[Session, Depends(get_db)] # dependency injection

# FastAPI routes

@app.get("/")
async def root():
    return {"openapi swagger":"http://127.0.0.1:8000/docs", "redoc":"http://127.0.0.1:8000/redoc"}

app.include_router(image.router)
app.include_router(garment.router)
app.include_router(outfit.router)
app.include_router(user.router)
app.include_router(auth.router)

app.include_router(gender.router)
app.include_router(category.router)
app.include_router(type.router)
app.include_router(color.router)
app.include_router(season.router)
app.include_router(usage.router)
