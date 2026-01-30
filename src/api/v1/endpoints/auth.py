from fastapi import APIRouter

router = APIRouter()

from pydantic import BaseModel
class TempData(BaseModel):
    pass

@router.post("/register", response_model=TempData)
async def register(db: TempData, credentials: TempData):
    return None

@router.post("/login", response_model=TempData)
async def login(db: TempData, credentials: TempData):
    return None

@router.post("/google", response_model=TempData)
async def google(db: TempData, credentials: TempData):
    return None