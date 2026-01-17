from fastapi import APIRouter

router = APIRouter()

from pydantic import BaseModel
class TempData(BaseModel):
    pass

@router.post("/email", response_model=TempData)
async def login_email(db: TempData, credentials: TempData):
    return None