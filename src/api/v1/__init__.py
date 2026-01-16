from fastapi import APIRouter

from .endpoints import user

router = APIRouter()
router.include_router(user.router, prefix="/users", tags=["users"])
