from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Annotated
import uuid, os

from ..database import get_db
from .. import models, schemas, oauth2
from ..config import config

PATH_FILES_STORAGE = config["PATH_FILES_STORAGE"]
PATH_FILES_STORAGE_IMAGE_SUBDIR = config["PATH_FILES_STORAGE_IMAGE_SUBDIR"]

PATH_TO_IMAGES = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_IMAGE_SUBDIR)

if not os.path.exists(PATH_TO_IMAGES):
    os.makedirs(PATH_TO_IMAGES)

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    tags=["images"],
    prefix="/images"
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ImageInfoResponse)
async def upload_image_file(
    file_in: UploadFile,
    db: db_dependency, 
    current_user: models.User = Depends(dependency=oauth2.get_current_user)
):
    filename_orig = file_in.filename
    extention = filename_orig.split('.')[-1]
    name = uuid.uuid4()
    filename: str = f'{name}.{extention}'

    full_path = os.path.join(PATH_TO_IMAGES, filename)
    with open(full_path, "wb") as f:
        f.write(file_in.file.read())

    image_info = models.ImageInfo(
        filename_store=filename,
        filename_original=filename_orig,
        user_id=current_user.id
    )
    db.add(image_info)
    db.commit()

    return image_info

@router.get("/{filename}")
async def get_image_file(
    filename: str,
    db: db_dependency, 
    current_user: models.User = Depends(dependency=oauth2.get_current_user)
):
    image_info = db.query(models.ImageInfo).filter(models.ImageInfo.filename_store==filename).first()
    if not image_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if image_info.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    full_path = os.path.join(PATH_TO_IMAGES, filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(path=full_path)

@router.get("/{filename}/info", response_model=schemas.ImageInfoResponse)
async def get_image_file_info(
    filename: str,
    db: db_dependency, 
    current_user: models.User = Depends(dependency=oauth2.get_current_user)
):
    image_info = db.query(models.ImageInfo).filter(models.ImageInfo.filename_store==filename).first()
    if not image_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if image_info.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return image_info
