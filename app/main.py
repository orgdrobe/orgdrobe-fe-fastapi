from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from typing import Annotated

# from my files
from .config import config
from .database import engine, get_db
from . import models
from .routers import user, garment, auth, outfit, image, gender, category, garment_type, color, season, usage, outfit_template
from .seed_data import initialize_table, initialize_ml_mapping_table, initialize_outfit_templates

SEED_DATA = config["SEED_DATA"]

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

# Set up event listeners for seeding before table creation (before `create_all`)
if SEED_DATA == "yes":
    event.listen(models.User.__table__, 'after_create', initialize_table)
    event.listen(models.Gender.__table__, 'after_create', initialize_table)
    event.listen(models.CategoryMaster.__table__, 'after_create', initialize_table)
    event.listen(models.CategorySub.__table__, 'after_create', initialize_table)
    event.listen(models.GarmentType.__table__, 'after_create', initialize_table)
    event.listen(models.Color.__table__, 'after_create', initialize_table)
    event.listen(models.Season.__table__, 'after_create', initialize_table)
    event.listen(models.Usage.__table__, 'after_create', initialize_table)
    event.listen(models.MLMapping.__table__, 'after_create', initialize_ml_mapping_table)
    event.listen(models.OutfitTemplateParameter.__table__, 'after_create', initialize_outfit_templates)

try:
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
except Exception as e:
    print(f" Failed to enable pgvector: {e}")

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

app.include_router(outfit_template.router)

app.include_router(gender.router)
app.include_router(category.router)
app.include_router(garment_type.router)
app.include_router(color.router)
app.include_router(season.router)
app.include_router(usage.router)
