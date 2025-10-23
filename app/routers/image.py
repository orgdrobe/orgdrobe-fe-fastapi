from fastapi import APIRouter, HTTPException, UploadFile, status 
from fastapi.responses import FileResponse
import uuid, os

from ..config import config

PATH_FILES_STORAGE = config["PATH_FILES_STORAGE"]
PATH_FILES_STORAGE_IMAGE_SUBDIR = config["PATH_FILES_STORAGE_IMAGE_SUBDIR"]

PATH_TO_IMAGES = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_IMAGE_SUBDIR)

if not os.path.exists(PATH_TO_IMAGES):
    os.makedirs(PATH_TO_IMAGES)

router = APIRouter(
    tags=["images"],
    prefix="/images"
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_image_file(
    file_in: UploadFile, 
):
    filename_orig = file_in.filename
    extention = filename_orig.split('.')[-1]
    name = uuid.uuid4()
    filename = f'{name}.{extention}'

    full_path = os.path.join(PATH_TO_IMAGES, filename)
    with open(full_path, "wb") as f:
        f.write(file_in.file.read())

    return {"filename":f'{filename}'} 

@router.get("/{filename}")
async def get_image_file(
    filename: str
):
    full_path = os.path.join(PATH_TO_IMAGES, filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(path=full_path)
